# Ethos themes

All themes are published on the [Ethos-Feedback-Community repository](https://github.com/FrSkyRC/ETHOS-Feedback-Community/tree/26.1/lua/themes).

I also publish them here for convenience as you can find in the [releases](https://github.com/EthosCommunityFeedback/themes/releases) section each theme in a zip file.

You can try them in the VS Code simulator: clone or download this repository and add the following to your .vscode/settings.json:

```jsonc
{
    "ethos.release": "nightly26",
    "ethos.board": "X20PRO",
    "ethos.protocol": "FCC",
    "ethos-devtools.deploy": {
        "app": "themes",
        "multiApp": true
    }
}
```

Then open the simulator using "Deploy & Launch Sim" and select the theme you want to try.
