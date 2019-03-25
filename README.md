# StockChatbot

## Demo
<img src="https://github.com/markwzh/StockChatbot/blob/master/Chatbot.gif" height="600" width="270">

## Installation

### iexfinance
#### Installing iexfinance
```
$ pip3 install iexfinance
```
#### More information 
It is provided on https://github.com/addisonlynch/iexfinance

### Rasa-NLU
#### Pre-requisite
Install Microsoft VC++ Compiler: 

More information is provided on https://visualstudio.microsoft.com/visual-cpp-build-tools/

#### Installing Rasa-NLU
```
$ pip install rasa_nlu
```
After running codes that include training the model, Rasa NLU will automatically check whether you have 
all the required dependencies installed and remind the users of the missing ones.

#### More information 
It is provided on https://rasa.com/docs/nlu/installation/

### wxpy
#### Installing wxpy
```
$ pip install wxpy
```
#### More information 
It is provided on https://wxpy.readthedocs.io/zh/latest/#

## Operation
1. Download all required packages
2. Open ```chatbot.py``` in the suitable IDE
3. Run the scipts and a QR code will be generated
4. Scan the code with wechat and start chatting with the chatbot
5. Feel free to switch to chat with different friends by changing the following line
```
my_friend = bot.friends().search('Mono', sex=MALE)[0]
```
