from pkgutil import iter_modules, ModuleInfo, walk_packages, get_data
import geoapi.processes.processes as geoapi_processes

class BaseProcess():
    def __init__(self):
        self.id = ""
        self.version = "1.0"
        self.title = ""
        self.description = ""
        self.keywords = []
        self.jobControlOptions = []
        self.outputTransmission = []
        self.input = []

    def main(self, params):
        pass

def get_processes_list() -> list[BaseProcess]:
    processes_classes: list[BaseProcess] = []
    module = geoapi_processes
    for submodule in walk_packages(module.__path__):
        submodule_name = submodule.name
        module = submodule.module_finder.find_module(f'{submodule_name}').load_module(f'{submodule_name}')
        new_process: BaseProcess = module.Process()
        processes_classes.append(new_process)        
    return processes_classes

def get_process_by_id(id: str) -> BaseProcess:
    processes = get_processes_list()
    for p in processes:
        if id == p.id:
            return p
    return None