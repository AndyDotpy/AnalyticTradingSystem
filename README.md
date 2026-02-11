# Automated Trading Bot Using the Alpaca API

A python based algorithmic trading bot that retreieves market data to determine how it should execute trades through the Alpaca API.

## Overview

This project is currently under active development, it will be an automatic algorithmic based trading bot using Python and the Alpaca Market API to make paper trades.
Supports retreiving, analyzing historical data and current data. Handles pagination and order execution for paper environments.
Supports a terminal based user interface that allows the user to interact with orders, queues, data, encryption and security.

Bot is designed to:
- Retreive historical and most recent data (at one minute intervals)
- Handles API pagination through next_page_token
- Respects the API rate limit
- Execute market orders
- Track many symbols

## Features
- Multiple symbol historical and recent data requests
- Automatic pagination handling
- Rate limit aware request system
- Paper trading
- Modular structure
- Data persists after program ends

## Tech Stack
- Python 3.10
- Requests
- Fernet
- Alpaca Market Data API
- Alpaca Trading API

## Installation
1. Clone repository:
   git clone https://github.com/yourusername/AnalyticTradingSystem.git
2. Navigate to the directory:
   cd cloned_directory
3. Install dependencies:
   pip install -r requirements.txt

## Configuration
Run the program with python main.py.
Every time the program runs it will ask for an encryption key since this is the first time running it you will enter n as it has not been set yet.
Type d then enter to go into data options then k to enter your API and secret key, these will be saved in a serialized .pkl file.
(Optional but recommended) Type p then enter to navigate to the parent, type c then enter for encryption options, type g then enter to generate a key.
The string inside the single quotes is your key save it securly and type e then enter, then enter your encryption key then hit enter.
Next time you save your data all of it including API keys, queues, orders and other persisting data will be encrypted.

## Disclaimer
This project is for educational purposes only and does not constitute financial advice.
Trading financial instruments involves risk.

## Next Steps
- Finish the automation implementation
- Finish the trading strategy implementation
