import importlib.util
import sys
from pathlib import Path
from typing import Dict, Any, Optional

class PluginLoader:
    def __init__(self, logger):
        self.logger = logger
        self.plugins: Dict[str, Any] = {}
        self.plugin_folder = Path("community_plugins")
        
    def load_plugin(self, plugin_name: str) -> Optional[Any]:
        try:
            plugin_path = self.plugin_folder / f"{plugin_name}.py"
            
            if not plugin_path.exists():
                self.logger.error(f"Plugin {plugin_name} not found at {plugin_path}")
                return None
                
            spec = importlib.util.spec_from_file_location(plugin_name, plugin_path)
            if spec is None or spec.loader is None:
                self.logger.error(f"Could not load spec for plugin {plugin_name}")
                return None
                
            module = importlib.util.module_from_spec(spec)
            sys.modules[plugin_name] = module
            
            spec.loader.exec_module(module)
            
            if not hasattr(module, 'Plugin'):
                self.logger.error(f"Plugin {plugin_name} does not have required Plugin class")
                return None
                
            plugin_instance = module.Plugin(self.logger)
            self.plugins[plugin_name] = plugin_instance
            self.logger.info(f"Successfully loaded plugin: {plugin_name}")
            
            return plugin_instance
            
        except Exception as e:
            self.logger.error(f"Error loading plugin {plugin_name}: {e}")
            return None
            
    def load_enabled_plugins(self, enabled_plugins: list) -> None:
        for plugin_name in enabled_plugins:
            if not plugin_name.startswith('cplugin_'):
                self.logger.warning(f"Skipping {plugin_name} - must start with 'cplugin_'")
                continue
                
            self.load_plugin(plugin_name)
            
    def get_loaded_plugins(self) -> Dict[str, Any]:
        return self.plugins
        
    def call_plugin_method(self, method_name: str, *args, **kwargs) -> list:
        for plugin_name, plugin in self.plugins.items():
            if hasattr(plugin, method_name):
                try:
                    method = getattr(plugin, method_name)
                    result = method(*args, **kwargs)
                    if result:
                        self.logger.info(f"Plugin {plugin_name} processed successfully")
                    else:
                        self.logger.info(f"Plugin {plugin_name} failed to process with result: {result}")
                except Exception as e:
                    self.logger.error(f"Error calling {method_name} on plugin {plugin_name}: {e}")