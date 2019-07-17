class BSMError(Exception):
    '''Basic exception for BSM'''


class LoadError(BSMError):
    '''Basic exception for loader'''

class LoadModuleError(LoadError):
    '''Exception when loading module'''

class AttributeNotFoundError(LoadError):
    '''Exception when attribute is not found in a module'''

class FunctionNotFoundError(AttributeNotFoundError):
    '''Exception when function is not found in a module'''

class NotCallableError(LoadError):
    '''Exception when the object found is not callable'''

class ClassNotFoundError(AttributeNotFoundError):
    '''Exception when class is not found in a module'''

class NotAClassError(LoadError):
    '''Exception when the object found is not a class'''


class GitError(BSMError):
    '''Basic exception for executing git'''

class GitNotFoundError(GitError):
    '''Exception when git command is not found'''

class GitUnknownCommandError(GitError):
    '''Exception when do not know how to execute git sub command'''

class GitEmptyUrlError(GitError):
    '''Exception when git url is not found'''


class ConfigError(BSMError):
    '''Basic exception dealing with yaml configuration'''

class ConfigLoadError(ConfigError):
    '''Exception when loading yaml configuration'''

class ConfigDumpError(ConfigError):
    '''Exception when dumping yaml configuration'''


class HandlerError(BSMError):
    '''Basic exception dealing with handler'''

class HandlerNotFoundError(HandlerError):
    '''Exception when specified handler is not found'''

class HandlerNotAvailableError(HandlerError):
    '''Exception when specified handler is not available. Should be thrown from handler'''


class PropError(BSMError):
    '''Basic exception for prop'''

class PropNotFoundError(PropError):
    '''Exception when requested prop is not found'''

class PropNotValidError(PropError):
    '''Exception when requested prop is not valid'''

class PropCategoryError(PropNotValidError):
    '''Exception when prop category is not valid'''

class PropPackageError(PropNotValidError):
    '''Exception when prop package is not valid'''

class PropPackageParamError(PropPackageError):
    '''Exception when prop package param is not valid'''

class PropReleaseVersionError(PropNotValidError):
    '''Exception when prop release version is not valid'''

class PropReleaseSettingError(PropNotValidError):
    '''Exception when prop release setting is not valid'''

class PropReleaseInstallError(PropNotValidError):
    '''Exception when prop release install is not valid'''


class OperationError(BSMError):
    '''Basic exception for operation'''

class OperationNotFoundError(OperationError):
    '''Exception when specified operation is not found'''

class OperationExecutionError(OperationError):
    '''Exception in operation execution'''

class OperationInstallExecutorError(OperationExecutionError):
    '''Exception in install executor'''

class OperationInstallReleaseError(OperationExecutionError):
    '''Exception in operation install-release'''

class OperationCreatePackagePropError(OperationExecutionError):
    '''Exception in operation create-package-prop'''

class OperationInstallPackagePropError(OperationExecutionError):
    '''Exception in operation install-package-prop'''

class OperationParsePackageParamError(OperationExecutionError):
    '''Exception in operation parse-package-param'''
