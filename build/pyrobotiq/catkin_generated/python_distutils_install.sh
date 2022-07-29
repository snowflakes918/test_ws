#!/bin/sh

if [ -n "$DESTDIR" ] ; then
    case $DESTDIR in
        /*) # ok
            ;;
        *)
            /bin/echo "DESTDIR argument must be absolute... "
            /bin/echo "otherwise python's distutils will bork things."
            exit 1
    esac
fi

echo_and_run() { echo "+ $@" ; "$@" ; }

echo_and_run cd "/home/difadmin/test_ws/src/pyrobotiq"

# ensure that Python install destination exists
echo_and_run mkdir -p "$DESTDIR/home/difadmin/test_ws/install/lib/python3/dist-packages"

# Note that PYTHONPATH is pulled from the environment to support installing
# into one location when some dependencies were installed in another
# location, #123.
echo_and_run /usr/bin/env \
    PYTHONPATH="/home/difadmin/test_ws/install/lib/python3/dist-packages:/home/difadmin/test_ws/build/lib/python3/dist-packages:$PYTHONPATH" \
    CATKIN_BINARY_DIR="/home/difadmin/test_ws/build" \
    "/usr/bin/python3" \
    "/home/difadmin/test_ws/src/pyrobotiq/setup.py" \
    egg_info --egg-base /home/difadmin/test_ws/build/pyrobotiq \
    build --build-base "/home/difadmin/test_ws/build/pyrobotiq" \
    install \
    --root="${DESTDIR-/}" \
    --install-layout=deb --prefix="/home/difadmin/test_ws/install" --install-scripts="/home/difadmin/test_ws/install/bin"
