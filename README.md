# tfdeb
![ci](https://github.com/joonvena/tfdeb/actions/workflows/ci.yml/badge.svg)

Simple updater for your Terraform versions.tf files.


## Variables

| Variable    			| Description 			 						            | Default                            |
| --------------------- | --------------------------------------------------------- |------------------------------------|          
| TF_REGISTRY_BASE_URL  | Base url where to fetch registry information              | "https://registry.terraform.io/v1" |
| TF_VERSIONS_FILE_PATH | Path to versions.tf file in repository     			    | "versions.tf"                      |
| GITLAB_URL            | Gitlab instance url                                       | "https://gitlab.com"               |
| GITLAB_PROJECT        | Path to project eg. <repository_owner>/<project_name>     | ""                                 |
| GITLAB_TOKEN          | Token that has full access to the project     			| ""                                 |
| GITHUB_TOKEN          | Token with read access to the public repositories         | ""                                 |
| BRANCH                | Branch you want to update     							| "master"                           |
