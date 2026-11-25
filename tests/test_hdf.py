import pytest
from urllib.parse import urlparse


@pytest.fixture
def aws_file():
    return {
        "path": "s3://modelers-data-bucket/eapp/single/ETH_flow_sim.h5",
        "file_size": 7374454,
        "dataset_name": "BR_Kabura",
        "dataset_size": 12784,
        "dataset_type": "float64"
    }


class TestHdf():
    def test_get_hdf_dataset_info(self, client, aws_file):
        """
          Does retrieved dataset info match the expected values?
        """
        ret = client.call("get_hdf_dataset_info", {'url': aws_file["path"], 'dataset_name': aws_file["dataset_name"]})
        assert ret == {'name': 'BR_Kabura', 'size': 12784, 'dtype': 'float64'}

    def test_get_hdf_dataframe(self, client, aws_file):
        """
          Is the correct segment of datset retrieved?
        """
        df = client.call("get_hdf_dataframe", {'url': aws_file["path"], 'dataset_name': aws_file["dataset_name"], 'start':8, 'end':16})
        assert df == {"BR_Kabura":{"63763200000":0.65664,
                                   "63849600000":0.65664,
                                   "63936000000":0.65664,
                                   "64022400000":0.65664,
                                   "64108800000":0.65664,
                                   "64195200000":0.65664,
                                   "64281600000":0.65664,
                                   "64368000000":0.65664}
                     }

    def test_get_hdf_filesize(self, client, aws_file):
        """
          Does the reported size of an HDF file match the expected value?
        """
        ret = client.call("get_hdf_filesize", {'url': aws_file["path"]})
        assert ret == aws_file['file_size']

    def test_resolve_s3_url_to_path(self, client, aws_file):
        """
          Does an s3:// url map correctly to a file in s3 storage?
          Note that this should be a noop.
        """
        path = client.call("resolve_url_to_path", {'url': aws_file["path"]})
        assert path == aws_file["path"]

    def test_resolve_filestore_url_to_path(self, client, aws_file):
        """
          Is a relative url correctly rewritten to map to a path in the HDF filestore?
          This uses on the 'path' portion of a url, stripping the leading '/' to make
          it relative, and then verifies that the resolver has correctly returned an
          absolute path.
        """
        path_only = urlparse(aws_file['path']).path.strip('/')
        filestore_path = client.call("resolve_url_to_path", {'url': path_only})
        assert filestore_path.startswith('/')

    def test_file_exists_at_url(self, client, aws_file):
        """
          Does the url of an existing file return the expected Boolean?
        """
        exists = client.call("file_exists_at_url", {'url': aws_file["path"]})
        assert exists
        exists = client.call("file_exists_at_url", {'url': "nonexist.h5"})
        assert not exists
