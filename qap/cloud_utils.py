# cloud_utils.py
#
# Contributing authors: Daniel Clark, Steve Giavasis, 2015


def download_single_s3_path(s3_path, cfg_dict):
    """Download a single file from an AWS s3 bucket.

    :type s3_path: str
    :param s3_path: An "s3://" pre-pended path to a file stored on an
                    Amazon AWS s3 bucket.
    :type cfg_dict: dictionary
    :param cfg_dict: A dictionary containing the pipeline setup
                     parameters.
    :rtype: str
    :return: The local filepath of the downloaded s3 file.
    """

    import os
    from indi_aws import fetch_creds, aws_utils

    # Init variables
    working_dir = cfg_dict["working_directory"]
    try:
        creds_path = cfg_dict["creds_path"]
    except KeyError:
        creds_path = None

    if "s3://" in s3_path:
        s3_prefix = s3_path.replace("s3://", "")
    else:
        err = "[!] S3 filepaths must be pre-pended with the 's3://' prefix."
        raise ValueError(err)

    bucket_name = s3_prefix.split("/")[0]
    bucket = fetch_creds.return_bucket(creds_path, bucket_name)

    data_dir = s3_path.split(bucket_name + "/")[1]
    local_dl = os.path.join(working_dir, data_dir)

    if os.path.isfile(local_dl):
        print("\nS3 bucket file already downloaded! Skipping download.")
        print("S3 file: {0}".format(s3_path))
        print("Local file already exists: {0}\n".format(local_dl))
    else:
        aws_utils.s3_download(bucket, ([data_dir], [local_dl]))

    return local_dl


def copy_directory_to_s3(from_path, to_path, cfg):
    """
    Copy the contents of a directory to S3

    :param from_path: the local path to copy data from
    :param to_path: the S3 path to copy data to
    :param cfg: pipeline configuration dictionary containing AWS credentials, if any
    :return:
    """

    # Import packages
    from indi_aws import aws_utils, fetch_creds
    import os

    if "s3://" not in to_path.lower():
        raise ValueError("Destination path {0} does not appear to be a correctly formatted S3 path.".format(to_path))

    bucket_name = to_path.replace('s3://', '').split('/')[0]

    bucket = fetch_creds.return_bucket(cfg["s3_write_credentials"], bucket_name)

    # And upload data
    upl_files = []
    for root, dirs, files in os.walk(from_path):
        if files:
            upl_files.extend([os.path.join(root, fil) for fil in files])

    # Using INDI AWS utils
    s3_upl_files = [ufile.replace(from_path, to_path) for ufile in upl_files]

    aws_utils.s3_upload(bucket, (upl_files, s3_upl_files))


def upl_qap_output(cfg_file):
    """Upload a pipeline output file to an AWS S3 bucket.

    :type cfg_file: str
    :param cfg_file: Filepath to the pipeline configuration file containing
                     S3 bucket and AWS credentials information.
    """

    # Import packages
    from indi_aws import aws_utils, fetch_creds
    import os
    import yaml

    # Load config file
    with open(cfg_file, 'r') as f:
        cfg_dict = yaml.load(f)

    # Init variables
    bucket_name = cfg_dict["bucket_name"]
    bucket_out_prefix = cfg_dict["bucket_prefix"]
    creds_path = cfg_dict["creds_path"]
    
    bucket = fetch_creds.return_bucket(creds_path, bucket_name)
        
    output_dir = cfg_dict['output_directory']

    # And upload data
    upl_files = []
    for root, dirs, files in os.walk(output_dir):
        if files:
            upl_files.extend([os.path.join(root, fil) for fil in files])

    # Using INDI AWS utils
    s3_upl_files = [ufile.replace(output_dir, bucket_out_prefix) for ufile in upl_files]

    aws_utils.s3_upload(bucket, (upl_files, s3_upl_files))
