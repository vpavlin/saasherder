import os
#import pytest
import tempfile
import anymarkup
from saasherder import SaasHerder
from shutil import copyfile

service_dir = "tests/data/service"
templates_dir = "tests/data/template"
output_dir = tempfile.mkdtemp()

temp_dir = tempfile.mkdtemp()
temp_path = os.path.join(temp_dir, "config.yaml")
  
class TestTemplating(object):
  def setup_method(self, method):
    # Start from fresh config.yaml
    copyfile("tests/data/config.yaml", temp_path)

  def test_template_hash(self):
    hash = "abcdef"
    se = SaasHerder(temp_path, None)
    se.template("tag", "redirector", output_dir, local=True)
    data = anymarkup.parse_file(os.path.join(output_dir, "redirector.yaml"))
    for item in data["items"]:
      if item["kind"] == "DeploymentConfig":
        assert item["spec"]["template"]["spec"]["containers"][0]["image"].endswith(hash)

  def test_template_hash_length(self):
    hash = "abcdef7"
    se = SaasHerder(temp_path, None)
    se.template("tag", "hash_length", output_dir, local=True)
    data = anymarkup.parse_file(os.path.join(output_dir, "hash_length.yaml"))
    for item in data["items"]:
      if item["kind"] == "DeploymentConfig":
        assert item["spec"]["template"]["spec"]["containers"][0]["image"].endswith(hash)

  def test_template_parameters(self):
    image = "some_image"
    se = SaasHerder(temp_path, None)
    se.template("tag", "redirector", output_dir, local=True)
    data = anymarkup.parse_file(os.path.join(output_dir, "redirector.yaml"))
    for item in data["items"]:
      if item["kind"] == "DeploymentConfig":
        assert item["spec"]["template"]["spec"]["containers"][0]["image"].startswith(image)

  def test_template_environment_parameters(self):
    image = "production_image"
    environment = "production"
    se = SaasHerder(temp_path, None, environment)
    se.template("tag", "redirector", output_dir, local=True)
    data = anymarkup.parse_file(os.path.join(output_dir, "redirector.yaml"))
    for item in data["items"]:
      if item["kind"] == "DeploymentConfig":
        assert item["spec"]["template"]["spec"]["containers"][0]["image"].startswith(image)

  def test_template_environment_skip(self):
    environment = "test"
    output_dir = tempfile.mkdtemp()
    se = SaasHerder(temp_path, None, environment)
    se.template("tag", "redirector", output_dir, local=True)
    assert not os.path.isfile(os.path.join(output_dir, "redirector.yaml"))

  def test_template_environment_url(self):
    environment = "url"
    output_dir = tempfile.mkdtemp()
    se = SaasHerder(temp_path, None, environment)
    assert se.get_services("redirector")[0]["url"] != "some_url"

  def test_template_environment_no_parameters(self):
    environment = "no_params"
    output_dir = tempfile.mkdtemp()
    se = SaasHerder(temp_path, None, environment)
    se.template("tag", "hash_length", output_dir, local=True)
    data = anymarkup.parse_file(os.path.join(output_dir, "hash_length.yaml"))
    for item in data["items"]:
      if item["kind"] == "DeploymentConfig":
        assert item["spec"]["replicas"] == 200