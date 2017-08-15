class Bundle(object):
    def __init__(self, bundle_root):
        self.__bundle_root = bundle_root

    def install(self, package):
        safe_mkdir(self.__bundle_root)
        self.__save_package_config(package_config)

        pacakge_root = os.path.join(self.__bundle_root, k)
        package = Package(k, v)
        package.check_local()
        if status == 'EMPTY':
            package.download()
        if status == '':
            package.download()
            package.extract()
            package.configure()
            package.compile()
            package.install()
            package.check()
            package.clean()

    def use(self):
        pass

    def __save_package_config(self, package_config):
        config_path = os.path.join(self.__bundle_root, '.cepcenv.pkg')
        if not os.path.exists(package_config):
            directory = os.path.dirname(dst)
            safe_mkdir(directory)
        shutil.copy2(src, dst)
