#!/usr/bin/python
# Copyright (c) 2022-present Sparky Studios. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
This script is used to help automate the generation of O3DE materials using the
StandardPBR material type from textures files.

Texture files ares assumed to have the following naming conventions:
- _ao: Ambient Occlusion
- _cavity: Specular Cavity Map
- _albedo: Diffuse Color Map
- _displacement: Displacement/Height/Parallax Map
- _emissive: Emissive Map
- _metalness: Metalness Map
- _normal: Normal Map
- _roughness: Roughness Map

Texture files are assumed to have the TIFF (.tiff) extension.
"""

import getopt
import json
import os
import sys


class BuildConfig:
    export_occ: bool = False
    export_cav: bool = False
    export_dif: bool = False
    export_dis: bool = False
    export_emi: bool = False
    export_met: bool = False
    export_ddn: bool = False
    export_rou: bool = False

    input_file_name: str = ''
    output_file_name: str = ''

    textures_dir_path: str = os.getcwd()
    assets_root_path: str = 'Assets'


def main(argv):
    config: BuildConfig = BuildConfig()
    verbose: bool = False

    try:
        opts, args = getopt.getopt(argv, "hvf:o:d:a:",
                                   ["occ", "cav", "dif", "dis", "emi", "met", "ddn", "rou", "default", "all"])
    except getopt.GetoptError:
        error()
        sys.exit(1)

    if len(opts) == 0:
        help()
        sys.exit()

    for opt, arg in opts:
        if opt == '-h':
            help()
            sys.exit()
        elif opt == '-v':
            verbose = True
        elif opt == '-f':
            config.input_file_name = arg
        elif opt == '-o':
            config.output_file_name = arg
        elif opt == '-d':
            config.textures_dir_path = arg
        elif opt == '-a':
            config.assets_root_path = arg
        elif opt == '--occ':
            config.export_occ = True
        elif opt == '--cav':
            config.export_cav = True
        elif opt == '--dif':
            config.export_dif = True
        elif opt == '--dis':
            config.export_dis = True
        elif opt == '--emi':
            config.export_emi = True
        elif opt == '--met':
            config.export_met = True
        elif opt == '--ddn':
            config.export_ddn = True
        elif opt == '--rou':
            config.export_rou = True
        elif opt == '--default':
            setup_default(config)
        elif opt == '--all':
            setup_all(config)

    if config.input_file_name == '':
        error()
        sys.exit(1)

    build(config, verbose)


def setup_default(config: BuildConfig):
    config.export_dif = True
    config.export_ddn = True
    config.export_occ = True
    config.export_met = True
    config.export_rou = True


def setup_all(config: BuildConfig):
    setup_default(config)
    config.export_emi = True
    config.export_cav = True
    config.export_dis = True


def build(config: BuildConfig, verbose: bool = False):
    maps = [('Ambient Occlusion', 'ao', 'occlusion.diffuseTextureMap', config.export_occ),
            ('Specular Cavity', 'cavity', 'occlusion.specularTextureMap', config.export_cav),
            ('Diffuse Color', 'albedo', 'baseColor.textureMap', config.export_dif),
            ('Height', 'displacement', 'parallax.textureMap', config.export_dis),
            ('Emissive', 'emissive', 'emissive.textureMap', config.export_emi),
            ('Metallic', 'metalness', 'metallic.textureMap', config.export_met),
            ('Normal', 'normal', 'normal.textureMap', config.export_ddn),
            ('Roughness', 'roughness', 'roughness.textureMap', config.export_rou),
            ]

    material: dict = {
        "materialType": "Materials/Types/StandardPBR.materialtype",
        "materialTypeVersion": 4,
        "propertyValues": {}
    }

    def make_map_name(file_name: str, map_name: str):
        return os.path.join(file_name + '_' + map_name + '.tiff')

    def make_file_map_name(file_name: str, map_name: str):
        return os.path.join(config.textures_dir_path, make_map_name(file_name, map_name))

    def make_asset_map_name(map_name: str):
        return os.path.join(config.assets_root_path, make_map_name(config.output_file_name, map_name))

    def rename_texture_files():
        if config.output_file_name == '' or config.output_file_name == config.input_file_name:
            if verbose:
                print('    [V] Skipping texture files renaming.')

            # Make sure output_file_name = input_file_name
            config.output_file_name = config.input_file_name
            return

        if verbose:
            print('    [V] Renaming texture files...')

        for name, m, _, enabled in maps:
            if enabled:
                if os.path.exists(make_file_map_name(config.input_file_name, m)):
                    os.rename(make_file_map_name(config.input_file_name, m), make_file_map_name(config.output_file_name, m))
                else:
                    print(('    [E] The {name} Map was enabled, but the file {file}_{map}.tiff do not exists. ' +
                           'The file was not renamed.').format(
                        name=name, file=config.output_file_name, map=m))

        if verbose:
            print('    [V] Texture files renamed.')

    def make_material():
        for name, m, key, enabled in maps:
            if enabled:
                if os.path.exists(make_file_map_name(config.output_file_name, m)):
                    material['propertyValues'][key] = make_asset_map_name(m).replace("\\", '/')
                else:
                    print(('    [E] The {name} Map was enabled, but the file {file}_{map}.tiff do not exists. ' +
                           'The file was not added in the material.').format(
                        name=name, file=config.output_file_name, map=m))

    if verbose:
        print('[V] Building material file...')

    rename_texture_files()
    make_material()

    with open(os.path.join(config.textures_dir_path, config.output_file_name + '.material'), 'w') as material_file:
        json.dump(material, material_file)

    if verbose:
        print('[V] Material file build process complete.')


def error():
    print("Invalid arguments passed to the script.\n")
    help(True)


def help(no_logo: bool = False):
    if not no_logo:
        print("O3DE Material Generator for")


if __name__ == "__main__":
    main(sys.argv[1:])
