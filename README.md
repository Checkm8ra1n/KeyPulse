## KeyPulse

KeyPulse is Python tool for quickly show the ASCII code of the charcter that are you writing near your cursor.

## Running

Install the requirements with `pip3 install -r requirements.txt`

And just run `python3 main.py`

You can also download the application file from the releases

## Note for macOS

If you'd like to test the tool on mac, the tool works perfectly, but if you want to hide the Python icon from the dock, you'll have to use pyinstaller to make an app file and on the `info.plist` generated, you have to insert these strings:
```
<key>LSUIElement</key>
<string>1</string>
```

Also you'll have to grant Accessibility and Input Monitoring access to Terminal and Python from System Settings