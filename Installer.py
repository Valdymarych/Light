from cx_Freeze import Executable, setup

executables=[Executable(
        script="Optica.py",
        targetName="Optica.exe",
        base="Win32GUI",
        shortcutName='Optica',
        icon='lens.ico',
        shortcutDir='DesktopFolder',
    )
]
excludes=["tkinter","test","asyncio","email","html",
          "http","logging","multiprocessing","unittest","urllib",
          "xml","xmlrpc","pydoc_data","socket",'select']
zip_include_packages = ['collections', 'encodings', 'importlib','ctypes','pkg_resources']

options = {
    'build_exe': {
        'include_msvcr': True,
        'excludes':excludes,
        'zip_include_packages':zip_include_packages,
    }
}

setup(
      name="Optica",
      version="0.0.1",
      executables=executables,
      options=options,
)
