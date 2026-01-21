from PyInstaller.utils.hooks import (
    collect_submodules,
    collect_data_files,
    collect_dynamic_libs,
)

# Collect ALL mediapipe modules (including mediapipe.tasks.c)
hiddenimports = collect_submodules("mediapipe")

# Collect models/config files inside mediapipe
datas = collect_data_files("mediapipe", include_py_files=True)

# Collect native libs (.so/.dylib/.dll) that mediapipe needs
binaries = collect_dynamic_libs("mediapipe")