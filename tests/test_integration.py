from functools import partial
from xml.etree import cElementTree as ET

import pytest
import logging
import subprocess

from swid_generator.generators import swid_generator
from swid_generator.settings import DEFAULT_REGID, DEFAULT_ENTITY_NAME
from swid_generator.environments.dpkg_environment import DpkgEnvironment


def py26_check_output(*popenargs, **kwargs):
    """
    This function is an ugly hack to monkey patch the backported `check_output`
    method into the subprocess module.

    Taken from https://gist.github.com/edufelipe/1027906.

    """
    process = subprocess.Popen(stdout=subprocess.PIPE, *popenargs, **kwargs)
    output, unused_err = process.communicate()
    retcode = process.poll()
    if retcode:
        cmd = kwargs.get('args')
        if cmd is None:
            cmd = popenargs[0]
        error = subprocess.CalledProcessError(retcode, cmd)
        error.output = output
        raise error
    return output


class TestEnvironment(DpkgEnvironment):

    # Python 2.6 compatibility
    if 'check_output' not in dir(subprocess):
        # Ugly monkey patching hack ahead
        logging.debug('Monkey patching subprocess.check_output')
        subprocess.check_output = py26_check_output

    os_string = 'SomeTestOS'

    @staticmethod
    def get_os_string():
        return TestEnvironment.os_string

    @staticmethod
    def get_architecture():
        return 'i686'


### Template fixtures ###
@pytest.fixture
def zsh_deb_package_template():
    with open('tests/dumps/zsh_5.1.1-1ubuntu2_amd64-SWID-template.xml') as template_file:
        return ET.fromstring(template_file.read())


@pytest.fixture
def swid_tag_generator():
    env = TestEnvironment()
    kwargs = {
        'environment': env,
        'entity_name': DEFAULT_ENTITY_NAME,
        'regid': DEFAULT_REGID
    }
    return partial(swid_generator.create_swid_tags, **kwargs)


def test_generate_swid_from_package(swid_tag_generator):
    output = list(swid_tag_generator(full=True, file_path="tests/dumps/zsh_5.1.1-1ubuntu2_amd64.deb"))
    output_root = ET.fromstring(output[0])

    template_root = zsh_deb_package_template()

    print(output_root)
    print(template_root)

    output_package_name = output_root.attrib['name']
    output_meta_tag = output_root[1]
    output_payload = output_root[2]

    template_package_name = template_root.attrib['name']
    template_meta_tag = template_root[1]
    template_payload = template_root[2]

    assert output_package_name == template_package_name

    assert output_meta_tag.attrib['product'] == template_meta_tag.attrib['product']

    assert len(output_payload) == len(template_payload)

    payload_size = len(output_payload)
    for i in range(0, payload_size):

        output_directory_tag = output_payload[i]
        template_directory_tag = template_payload[i]

        output_directory_fullpath = output_directory_tag.attrib['root'] + "/" + output_directory_tag.attrib['name']
        template_directory_fullpath = template_directory_tag.attrib['root'] + "/" + template_directory_tag.attrib['name']

        assert output_directory_fullpath == template_directory_fullpath
        print("directory ", output_directory_fullpath, " ----- ", template_directory_fullpath)

        assert len(output_directory_tag) == len(template_directory_tag)

        directory_tag_size = len(output_directory_tag)

        for j in range(0, directory_tag_size):
            assert output_directory_tag[j].attrib['name'] == template_directory_tag[j].attrib['name']
            print("name ", output_directory_tag[j].attrib['name'], " ----- ", template_directory_tag[j].attrib['name'])
            assert output_directory_tag[j].attrib['size'] == template_directory_tag[j].attrib['size']