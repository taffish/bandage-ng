#!/usr/bin/python3
"""Packaging self-checks: private sessions, negative RFB tests, and endpoint ownership during very early or forced termination."""
import importlib.machinery
import importlib.util
import os
from pathlib import Path
import signal
import socket
import stat
import sys
import tempfile
import threading
import time

sys.dont_write_bytecode = True
loader = importlib.machinery.SourceFileLoader('gui', '/usr/local/bin/bandage-ng-gui')
spec = importlib.util.spec_from_loader('gui', loader)
gui = importlib.util.module_from_spec(spec)
loader.exec_module(gui)
spec = importlib.util.spec_from_file_location('rfb', '/usr/local/libexec/bandage-ng/rfb-probe.py')
rfb = importlib.util.module_from_spec(spec)
spec.loader.exec_module(rfb)


def args(display):
    sys.argv = ['session-contract', '--display', display, '--port', '16181', '--vnc-port', '16182']
    return gui.arguments()


def privacy():
    roots = []
    before = os.umask(0)
    os.umask(before)
    for mask in (0, 0o077):
        os.umask(mask)
        session = gui.Session(args(':1261'))
        roots.append(session.root)
        assert stat.S_IMODE(session.root.stat().st_mode) == 0o700
        for name in ['home', 'config', 'cache', 'runtime', 'tmp']:
            assert stat.S_IMODE((session.root / name).stat().st_mode) == 0o700
        observed = os.umask(mask)
        assert observed == mask
        session.cleanup()
    os.umask(before)
    assert len(set(roots)) == 2
    # Preserve foreign locks and broken symlinks; remove only sentinels created by this probe.
    endpoint = Path('/tmp/.X1262-lock')
    assert not os.path.lexists(endpoint)
    for link in (False, True):
        if link:
            endpoint.symlink_to('/tmp/bandage-contract-nonexistent')
        else:
            endpoint.write_text('foreign-sentinel')
        identity = endpoint.lstat()
        session = gui.Session(args(':1262'))
        try:
            session.serve()
            raise AssertionError('accepted occupied endpoint')
        except RuntimeError as error:
            assert 'occupied display endpoint' in str(error)
        finally:
            session.cleanup()
        assert endpoint.lstat().st_ino == identity.st_ino
        assert os.path.islink(endpoint) if link else endpoint.read_text() == 'foreign-sentinel'
        endpoint.unlink()
    print('privacy PASS: umask unchanged, unique 0700 roots, foreign/symlink unchanged')


def protocol():
    for payload in (b'', b'NOT RFB DATA\n', b'RFB 003.008\n'):
        with socket.socket() as listener:
            listener.bind(('127.0.0.1', 0))
            listener.listen()
            def serve():
                conn, _ = listener.accept()
                with conn:
                    if payload:
                        conn.sendall(payload)
                    time.sleep(0.3)
            worker = threading.Thread(target=serve)
            worker.start()
            try:
                rfb.probe(listener.getsockname()[1], 1440, 900, timeout=0.15)
                raise AssertionError('accepted silent/malformed/incomplete RFB')
            except (OSError, ValueError):
                pass
            worker.join(timeout=2)
            assert not worker.is_alive()
    print('protocol PASS: silent, malformed and incomplete endpoints rejected')


def early():
    # Local endpoint-timing fixture; not a replacement for real wrapper/Xvfb backend acceptance.
    for number, sig, forced in [(1263, signal.SIGINT, False), (1264, signal.SIGTERM, False), (1265, signal.SIGTERM, True)]:
        lock = Path(f'/tmp/.X{number}-lock')
        sock = Path(f'/tmp/.X11-unix/X{number}')
        assert not os.path.lexists(lock) and not os.path.lexists(sock)
        sock.parent.mkdir(exist_ok=True)
        session = gui.Session(args(':' + str(number)))
        code = f"import os,socket,time; from pathlib import Path; Path({str(lock)!r}).write_text(str(os.getpid())); s=socket.socket(socket.AF_UNIX); s.bind({str(sock)!r}); time.sleep(30)"
        session.start('xvfb', ['python3', '-c', code])
        if forced:
            deadline = time.monotonic() + 3
            while not sock.is_socket():
                assert time.monotonic() < deadline
                time.sleep(0.01)
            session.capture_endpoints()
            os.kill(session.children['xvfb'].pid, signal.SIGKILL)
        session.on_signal(sig, None)
        session.cleanup()
        assert not os.path.lexists(lock) and not os.path.lexists(sock)
        assert session.children['xvfb'].poll() is not None
    print('early PASS: INT/TERM before registration and forced-kill ownership cleanup')


{'privacy': privacy, 'protocol': protocol, 'early': early}[sys.argv[1]]()
