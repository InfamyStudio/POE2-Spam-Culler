# POE2 Spam Culler:

A community-driven framework for detecting and managing spam messages in Path of Exile 2, with a focus on identifying RMT (Real Money Trading) attempts and other harmful spam patterns.
POE2 Spam Culler, also supports a fully customisable framework allowing for any community plugin to be created/integrated.

[Join our Discord community for support and discussion](https://discord.gg/VDdrpSVpSx)

## Overview:

POE2 Spam Culler is designed to monitor the Path of Exile 2 client logs in real-time, identifying potential spam messages using configurable pattern matching. The tool currently detects:
- Suspicious URLs and known spam domains
- Discord handles used for RMT
- Currency trade offers involving real money
- Suspicious coupon codes and discounts

POE2 Spam Culler also provides a smart community based plugin loading system allowing anyone to create plugins for the framework to handle any manner of tasks.

This project aims to serve as a foundation for community-driven spam protection in POE2, allowing for collaborative development of more sophisticated spam detection and management solutions.

## Current Core Features:

- Real-time monitoring of POE2 client logs
- Pattern-based spam detection using regex
- Configurable spam domains and Discord handle lists
- Detailed logging with rotation support
- Support for multiple spam detection criteria:
  - URL pattern matching
  - Discord username detection
  - Currency offer identification
  - Coupon code detection

## Contributing to Core:

Contributions are welcome! When contributing, please:

1. Fork the repository
2. Create a feature branch
3. Add detailed comments and documentation
4. Include debug logs where appropriate
5. Submit a pull request with a clear description of changes

## Creating your own Plugin:
- See [Example Plugin](https://github.com/InfamyStudio/POE2-Spam-Culler/blob/main/community_plugins/cplugin_example_plugin.py) for a template to create your own plugin.
1. Follow the above steps to fork the repository and have it running on your local machine.
2. Create a new python file in the community_plugins directory with the naming convention 'cplugin_your_plugin_name.py'
3. Create a class in the file with the naming convention 'Plugin'
4. Current supported plugin triggers are:
   - process_spam
5. Choose a supported trigger and name this as the main callable function in your class (Where all your core logic goes)
6. Add your plugin to the enabled plugins list in the config.json file
7. Submit a pull request with your plugin for review and inclusion in the repository

## Important Information:

- Currently the framework does not take any action, if you continue to read the below sections you will see why this is important.
- A few areas need to be worked out and different solutions can be implemented depending on different use cases.
- I propose a design where we create a modular system that allow a user to perform different actions based on spam detections leaving the framework open ended for the community to build upon.
- This would mean contributors can create "plugins" that allow a user to choose what action is taken on spam detection.
- Another point to note is the name of the file being client.py - The reason for this is in my own build the spam reports get transproted to a server which triggers discord embeds. This is purely a proof of concept and not included in this repository.

## Requirements:

- Python 3.12+
- Windows OS (due to pywin32 dependency)
- Path of Exile 2 installed

## Installation:

1. Clone the repository:
```bash
git clone https://github.com/InfamyStudio/POE2-Spam-Culler.git
cd poe2-spam-culler
```

2. Install required dependencies:
```bash
pip install -r requirements.txt

OR setup an env first:

python -m venv env
env\Scripts\activate
pip install -r requirements.txt
```

3. Edit `config.json` file in the root directory to your path to the POE2 client log file:
```json
{
    "log_path": "PATH_TO_YOUR_POE2_CLIENT_LOG" <- My path is in here currently to give guidance
    "plugins_enabled": [
        "cplugin_example_plugin" <- This is the example plugin, you can add as many plugins as you like to be enabled or even create your own
    ]
}
```

4. You can now modify the spam_hosts and spam_discord files to add your own spam domains and discord handles to monitor for:

## Usage:

Run the script:
```bash
python client.py
```

The tool will start monitoring your POE2 client logs for potential spam messages. Detected spam will be logged to `spam_monitor.log` and displayed in the console.

## Future Development and Community Contribution:

This project is intended as a framework that the community can build upon. Some key areas for development include:

### Open Questions to Solve:
1. **Spam Response Actions**
   - What actions should be taken when spam is detected?
   - Should detected spam be reported to game developers?
   - Implementation of auto-ignore features?

2. **Community List Management**
   - How to maintain shared spam lists?
   - Verification methods for spam reports
   - Prevention of false positives and list manipulation
   - Scale of list sharing (global vs group-based)

3. **Integration Possibilities**
   - Discord bot integration
   - Other community tools

## Known Limitations:

- Currently Windows-only due to pywin32 dependency
- Potential for false positives in message pattern matching
- No automatic actions on spam detection
- Basic pattern matching system could be improved
- No built-in spam list verification