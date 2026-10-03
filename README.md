## Requirements
To use this application, you will need:

* **Python 3.6+** (DO NOT USE PYTHON 2)
* **Cisco SD-WAN 18+**
* A **vManage Cisco SD-WAN account** with read or read/write depending on the action

## Features
Summary of the features/capabilities/actions:
  - **export**             Export entire configuration.
  - **configure**            Import entire configuration.
      - *For Templates and Polices dependencies to be preserved use this option (configure)*
  - **configure_policies**   Import policies, definitions and lists.
  - **configure_templates**  Import feature templates and device templates.
      - *Templates will be imported but dependencies to policies will not be imported*
  - **clean**                Delete template(all) and policy(all) configuration.
      - *For an accurate deploy of a configuration a clean up is required, in case of items named the same*
  - **clean_devices**        Delete certificates and system devices.
  - **clean_policies**       Delete (only) policies, definitions and lists.
  - **clean_templates**      Delete (only) device and feature templates.
      - *Devices should be manually detached before cleanup*
  - **password**                  Update user password
  - **add_user**                  Add user
  - **invalidate_certificates**   Invalidate device certificates
  - **validate_certificates**     Validate device certificates
  - **push_to_controllers**       Push configuration to controllers
  - **detach_devices**            Detach device templates
  - **deactivate_policies**       Deactivate policies

## Installation
Step-by-step series for how to install the project and its dependencies:
1. Clone the code to your local machine.

```
git clone https://github.com/gcwvictor/vmanage-backup-restore.git
cd vmanage-backup-restore
```

2. Setup Python Virtual Environment (requires Python 3 and Requests)

```
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

3. Get your Cisco SD-WAN
 - IP address of the vManage or the DNS name of the vManage.
 - Credentials (Username and Password)

4. GO to next sections (Help and Usage)

## Help

Investigate the built in help with:

```
python vmanage_tool.py --help
```
or
```
python vmanage_tool.py -h
```

OUTPUT:

```
usage: vmanage_tool.py [-h] [-tenant TENANT]

Command line tool for Cisco SD-WAN vManage configuration management.

Example: python vmanage_tool.py <vManage> <username> <password> <action>

Actions:
  export                      Export entire configuration.

  configure                   Import entire configuration.
  configure_policies          Import policies, definitions and lists.
  configure_templates         Import feature templates and device templates.

  clean                       Delete template(all) and policy(all) configuration.
  clean_policies              Delete (only) policies, definitions and lists.
  clean_templates             Delete (only) device and feature templates.

  clean_devices               Delete certificates and system devices.

  password                    Update user password
  add_user                    Add user

  invalidate_certificates     Invalidate device certificates
  validate_certificates       Validate device certificates
  push_to_controllers         Push configuration to controllers
  detach_devices              Detach device templates
  deactivate_policies         Deactivate policies

positional arguments:
  vManage               vManage IP address or DNS name
  username              Username to login the vManage
  password              Password to login the vManage
  action                Action to execute on the vManage
  configfile            Optional, specific export and import archive name

optional arguments:
  -h, --help            show this help message and exit
  -tenant TENANT, --tenant TENANT
                        Specify tenant in multi-tenant setup
```



## Usage

Basic example how to use the vManage Tool:

```
python vmanage_tool.py [vManage IP] [vManage Netadmin Role User] [vManage Password] export
```

Multi-tenant example how to use the vManage Tool:

```
python vmanage_tool.py [vManage IP] [vManage Netadmin Role User] [vManage Password] export -tenant mytenantname
```

Specific archive export example how to use the vManage Tool:

```
python vmanage_tool.py [vManage IP] [vManage Netadmin Role User] [vManage Password] export mysdwanarchive.tar.gz
```

Specific archive export example how to use the vManage Tool:

```
python parser.py
```

Specific archive import multi-tenant example how to use the vManage Tool:

```
python vmanage_tool.py [vManage IP] [vManage Netadmin Role User] [vManage Password] configure mysdwanarchive.tar.gz -tenant mytenantname
```

---

Basic example how to use the vManage Tool with DevNet Sandbox:

```
python vmanage_tool.py sandboxsdwan.cisco.com:8443 devnetuser Cisco123! export mysdwanarchive.tar.gz
```
```
python vmanage_tool.py sandboxsdwan.cisco.com:8443 devnetuser Cisco123! configure mysdwanarchive.tar.gz
```

---

Normal Workflow for Templates Only: export -> clean_templates -> configure_templates

NOTE: The clean action can be skipped if you want to keep existing configurations and it's not overlapping.  
```
python vmanage_tool.py <vManage> <username> <password> export
python vmanage_tool.py <vManage> <username> <password> clean_templates
python vmanage_tool.py <vManage> <username> <password> configure_templates
```

Normal Workflow for Policies Only: export -> clean_policies -> configure_policies

NOTE: The clean action can be skipped if you want to keep existing configurations and it's not overlapping.  
```
python vmanage_tool.py <vManage> <username> <password> export
python vmanage_tool.py <vManage> <username> <password> clean_policies
python vmanage_tool.py <vManage> <username> <password> configure_policies
```

Normal Workflow for Templates with Policies: export -> clean -> configure

NOTE: The clean action can be skipped if you want to keep existing configurations and it's not overlapping.  
```
python vmanage_tool.py <vManage> <username> <password> export
python vmanage_tool.py <vManage> <username> <password> clean
python vmanage_tool.py <vManage> <username> <password> configure
```

---

**NOTE:** The configuration archive will be exported to the same folder where the script is.

**NOTE:** When importing/configuring please have the configuration archive named config_backup.tar.gz(or the one used as parameter) in the same folder

**NOTE:** The configure option will not overwrite items(templates/policies) that have the same name, they will be skipped and the process will continue.


## Output

Basic output example for Cisco SD-WAN EXIM (Export and Import) with DevNet Sandbox:

```
Action:
export                    Export entire configuration.

device_template
Exporting ID: 72babaf2-68b6-4176-92d5-fa8de58e19d8
Successfully exported the device templates from sandboxsdwan.cisco.com:8443

feature_template
Exporting ID: b4012da9-79e5-49b7-9787-b6421d061fec
Successfully exported the feature templates from sandboxsdwan.cisco.com:8443

vedge_policy
Successfully exported the vEdge policies from sandboxsdwan.cisco.com:8443

vsmart_policy
Successfully exported the vSmart policies from sandboxsdwan.cisco.com:8443

vedge_policy_id
Successfully exported the vEdge policy IDs from sandboxsdwan.cisco.com:8443

vsmart_policy_id
Successfully exported the vSmart policy IDs from sandboxsdwan.cisco.com:8443

policy_definition
Exporting done for /cflowd
...
Exporting done for /rewriterule
Successfully exported the policy definitions from sandboxsdwan.cisco.com:8443

policy_list
Exporting done for /community
...
Exporting done for /vpn
Exporting ID: e116735d-8e96-41ce-a93b-21d8c7aa9c19
Successfully exported the policy lists from sandboxsdwan.cisco.com:8443

Successfully exported the configuration from sandboxsdwan.cisco.com:8443
```



## License

This project is licensed to you under the terms of the [Cisco Sample
Code License](./LICENSE).
