# POE2 Spam Culler

A community-driven framework for detecting and managing spam messages in Path of Exile 2, with a focus on identifying RMT (Real Money Trading) attempts and other harmful spam patterns.  
**POE2 Spam Culler** also supports a fully customisable framework, enabling the community to build and integrate any plugin they choose.

[Join our Discord community for support and discussion](https://discord.gg/VDdrpSVpSx)

---

## Overview

**POE2 Spam Culler** monitors the Path of Exile 2 client logs in real-time, using configurable pattern matching to identify potential spam messages. Its core detections currently include:

- Suspicious URLs and known spam domains  
- Discord handles commonly associated with RMT  
- Currency trade offers involving real money  
- Suspect coupon codes and discounts  

A smart community-based plugin loading system is also provided, allowing anyone to create and share plugins for handling tasks of all kinds. The goal is to establish a foundation for collaborative spam protection in POE2, where more advanced detection and management solutions can evolve.

---

## Current Core Features

- **Real-time log monitoring** of POE2 client logs  
- **Regex-based spam detection** for flexible pattern matching  
- **Configurable spam domains** and Discord handle lists  
- **Detailed logging** with rotation support  
- **Multiple spam detection criteria**:
  - URL pattern matching  
  - Discord username detection  
  - Currency offer identification  
  - Coupon code detection  

---

## Contributing to the Core

Contributions are welcome! To contribute:

1. Fork the repository.  
2. Create a feature branch.  
3. Add detailed comments and documentation to your changes.  
4. Include debug logs where appropriate.  
5. Submit a pull request with a clear description of your changes.

---

## Creating Your Own Plugin

For a working example, see the [Example Plugin](https://github.com/InfamyStudio/POE2-Spam-Culler/blob/main/community_plugins/cplugin_example_plugin.py).

1. Follow the steps above to fork the repository and get it running locally.  
2. Create a new Python file in the `community_plugins` directory, named `cplugin_your_plugin_name.py`.  
3. Inside that file, create a class named `Plugin`.  
4. Supported plugin triggers currently include:
   - `process_spam`  
5. Select a supported trigger and implement it as the main callable function in your class, containing your core plugin logic.  
6. Add your plugin to the `plugins_enabled` list in `config.json`.  
7. Submit a pull request with your plugin for review and inclusion.

---

## Important Information

- At present, the framework does not perform any actions automatically.  
- Further discussion is needed to decide how spam detections should be handled. Different communities may require different approaches.  
- To solve this issue, the system is build to be modular and allow for plugins to be enabled and disabled as needed. This means you can choose what action is taken for matched spam by either enabling a community plugin or creating your own.  
- The file is named `client.py` because, in my own build, spam reports are transported to a server that sends Discord embeds. This is only a proof of concept and is not included in this repository.

---

## Requirements

- Python 3.12+  
- Windows OS (due to pywin32 dependency)  
- Path of Exile 2 installed  

---

## Installation

1. **Clone the repository:**

   ```bash
   git clone https://github.com/InfamyStudio/POE2-Spam-Culler.git
   cd poe2-spam-culler
   ```
2. **Install required dependencies:**

   ```bash
   pip install -r requirements.txt

   # OR set up a virtual environment first:

   python -m venv env
   env\Scripts\activate
   pip install -r requirements.txt
   ```
3. **Edit the ```config.json``` file in the root directory to point to your POE2 client log file:**

   ```json
   {
      "log_path": "PATH_TO_YOUR_POE2_CLIENT_LOG",
      "plugins_enabled": [
         "cplugin_example_plugin"
      ]
   }
   ```
   Note: The example config includes my path and the example plugin for demonstration. Update these to suit your needs.
   You can also select what plugins to enable by adding them to the `plugins_enabled` list.
4. **Edit ```spam_hosts``` and ```spam_discord``` to maintain your own lists of suspicious hosts and Discord handles:**
- Example spam_hosts:
```
google
xyz
```
Note you do not need to include the full URL, just the domain name/host name. The system automatically checks for domain endings like .com, .net, etc.
- Example spam_discord:
```
user1
user2
```

---

## Usage
Run the script
   ```bash
   python client.py
   ```
The tool will begin monitoring your POE2 client logs for potential spam messages. Detections are recorded in ```spam_monitor.log``` and displayed in the console.

---

## Future Development and Community Contribution
This framework is intended to serve as a starting point for the community. Below are some areas needing further attention:
1. **Spam Response Actions**
- What actions should be taken when spam is detected?
- Should detected spam be automatically reported to the game developers?
- Implementation of auto-ignore features?
2. **Community List Management**
- How should shared spam lists be maintained?
- How do we verify spam reports?
- How do we prevent false positives or manipulation?
- Should lists be global or group-based?
3. **Integration Possibilities**
Possible Discord bot integration
Compatibility with other community tools

---

## Known Limitations
- Windows-only due to the pywin32 dependency.
- False positives may occur due to basic pattern matching.
- No automatic actions on spam detection yet.
- Regex-based detection can be improved.
- No built-in verification for spam lists.

---
Feel free to open issues, submit pull requests, or discuss new ideas on our [Discord channel](https://discord.gg/VDdrpSVpSx). Together, we can refine and expand POE2 Spam Culler into a powerful spam defence system for Path of Exile