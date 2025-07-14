# pylint: disable=missing-module-docstring,consider-using-from-import,import-error,unused-import
import asyncio

from viam.module.module import Module
import src.blurry_classifier_module

if __name__ == "__main__":
    asyncio.run(Module.run_from_registry())
