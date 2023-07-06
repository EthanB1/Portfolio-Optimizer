{
 "cells": [
  {
   "cell_type": "code",
   "execution_count": 3,
   "id": "fa274682-a960-4820-af41-6271b002e02f",
   "metadata": {
    "tags": []
   },
   "outputs": [],
   "source": [
    "from datetime import datetime, timedelta\n",
    "import os\n",
    "import requests\n",
    "import pandas as pd\n",
    "from dotenv import load_dotenv\n",
    "import alpaca_trade_api as tradeapi\n",
    "import hvplot.pandas\n",
    "\n",
    "def get_data60(number_of_years):\n",
    "\n",
    "    # load env\n",
    "    load_dotenv()\n",
    "\n",
    "    # Load Alpaca keys required by the APIs\n",
    "    alpaca_api_key = os.getenv('ALPACA_API_KEY')\n",
    "    alpaca_secret_key = os.getenv('ALPACA_SECRET_KEY')\n",
    "\n",
    "    # Create the Alpaca API object\n",
    "    alpaca_api = tradeapi.REST(\n",
    "        alpaca_api_key,\n",
    "        alpaca_secret_key,\n",
    "        api_version = 'v2'\n",
    "    )\n",
    "\n",
    "    # Set timeframe to \"1Day\" for Alpaca API\n",
    "    timeframe = \"1Day\"\n",
    "\n",
    "    # set the start,end date\n",
    "    today = datetime.today() - timedelta(days=1)\n",
    "    start = today - timedelta(days=365*number_of_years)\n",
    "\n",
    "    today = pd.Timestamp('2023-06-28',tz='America/New_York')\n",
    "    start = today - pd.Timedelta(365*number_of_years, 'd')\n",
    "\n",
    "    tickers = [ 'IEF', 'VCIT', 'NOBL', 'USMV' ]\n",
    "    #tickers = ['AGG','SPY']\n",
    "    # Get number_of_years' worth of historical data for tickers\n",
    "    data_df = alpaca_api.get_bars(\n",
    "        tickers,\n",
    "        timeframe,\n",
    "        start = start.isoformat(),\n",
    "        end = today.isoformat()\n",
    "    ).df\n",
    "\n",
    "    data_df.index = data_df.index.date\n",
    "\n",
    "    # Reorganize the DataFrame\n",
    "    # Separate ticker data\n",
    "    ief_df = data_df.loc[data_df['symbol']=='IEF']\n",
    "    vcit_df = data_df.loc[data_df['symbol']=='VCIT']\n",
    "    nobl_df = data_df.loc[data_df['symbol']=='NOBL']\n",
    "    usmv_df = data_df.loc[data_df['symbol']=='USMV']\n",
    "\n",
    "    # Concatenate the ticker DataFrames\n",
    "    return_df = pd.concat([ief_df['close'],vcit_df['close'],nobl_df['close'],usmv_df['close']],\n",
    "                          axis=1,join=\"inner\",keys=['IEF','VCIT','NOBL','USMV'])\n",
    "\n",
    "\n",
    "    # return data\n",
    "    return { 'weight' : [0.4, 0.3, 0.2, 0.1], 'data': return_df }"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 4,
   "id": "fe60fc6d-61b2-4ec0-bbfb-12ff107fb117",
   "metadata": {
    "tags": []
   },
   "outputs": [
    {
     "data": {
      "text/plain": [
       "{'weight': [0.4, 0.3, 0.2, 0.1],\n",
       " 'data':                IEF   VCIT   NOBL    USMV\n",
       " 2015-12-01  106.80  85.32  50.46  42.320\n",
       " 2015-12-02  106.50  85.10  49.95  41.920\n",
       " 2015-12-03  105.38  84.45  49.41  41.370\n",
       " 2015-12-04  105.77  84.74  50.30  42.200\n",
       " 2015-12-07  106.11  84.77  50.13  42.129\n",
       " ...            ...    ...    ...     ...\n",
       " 2023-06-22   96.70  78.75  92.28  73.380\n",
       " 2023-06-23   97.10  78.88  91.62  72.810\n",
       " 2023-06-26   97.34  79.05  92.43  72.980\n",
       " 2023-06-27   97.00  78.85  93.16  73.450\n",
       " 2023-06-28   97.39  79.20  92.72  73.070\n",
       " \n",
       " [1906 rows x 4 columns]}"
      ]
     },
     "execution_count": 4,
     "metadata": {},
     "output_type": "execute_result"
    }
   ],
   "source": [
    "get_data60(15)"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "5487819b-3aef-48a6-a1b2-7aa3ed20a716",
   "metadata": {},
   "outputs": [],
   "source": []
  }
 ],
 "metadata": {
  "kernelspec": {
   "display_name": "Python 3 (ipykernel)",
   "language": "python",
   "name": "python3"
  },
  "language_info": {
   "codemirror_mode": {
    "name": "ipython",
    "version": 3
   },
   "file_extension": ".py",
   "mimetype": "text/x-python",
   "name": "python",
   "nbconvert_exporter": "python",
   "pygments_lexer": "ipython3",
   "version": "3.10.9"
  }
 },
 "nbformat": 4,
 "nbformat_minor": 5
}
