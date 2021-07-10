"""
С датами, ценами, подачей заявки, местоположением:
https://zakupki.gov.ru/epz/order/extendedsearch/results.html?  
searchString=%D0%BB%D0%B8%D1%84%D1%82& - **ключевое слово**
morphology=on& - **хз для чего(пусть будет)**  
search-filter=%D0%94%D0%B0%D1%82%D0%B5+%D1%80%D0%B0%D0%B7%D0%BC%D0%B5%D1%89%D0%B5%D0%BD%D0%B8%D1%8F& - **Дата + Размещение**  
pageNumber=1&  
sortDirection=false& - **по уменьшению**  
recordsPerPage=_20& - **элементов на странице**  
showLotsInfoHidden=false&  
sortBy=UPDATE_DATE&  
fz44=on&
fz223=on&
af=on& - **Подача заявок** 
priceFromGeneral=10000000&
priceToGeneral=15000000&
currencyIdGeneral=-1&
publishDateFrom=18.05.2021&
applSubmissionCloseDateFrom=04.06.2021&
customerPlace=5277317&  - **местоположение**  
customerPlace=5277335%2C5277327& - **если 2 местороложения**
customerPlaceCodes=%2C&
"""

### To install
pip install airtable-python-wrapper
dateutil
BeautifullSoup
pandas
openpyxl
xlsxwriter

