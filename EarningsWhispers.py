"""This code scraps earnings reports"""


from email.mime.text import MIMEText
from PRIVATE_INFO import credential
from lxml import html
import smtplib
import requests
from bs4 import BeautifulSoup


def get_soup(url):
    page = requests.get(url)
    # Create a BeautifulSoup object
    soup = BeautifulSoup(page.text, 'html.parser')
    return soup

# get html resources
def get_tree(url=''):
    page = requests.get(url)
    tree = html.fromstring(page.content)
    return tree


# gets list of Tickers that has earnings for the specific date
def get_earnings_list(date='2019-02-25'):
    print(f'Getting the list of Tickers, which releases earnings on {date}...')
    ticker_array = []

    # Usually the number of earning reports per day is less than 200
    tree = get_tree(f'https://finance.yahoo.com/calendar/earnings?day={date}&offset=0&size=100')
    table = tree.xpath('//*[@id="cal-res-table"]/div[1]/table/tbody//text()')
    tree = get_tree(f'https://finance.yahoo.com/calendar/earnings?day={date}&offset=100&size=100')
    table += tree.xpath('//*[@id="cal-res-table"]/div[1]/table/tbody//text()')

    for i in table:
        if i.isupper() and 'N/A' not in i and i not in ticker_array and len(i) < 7:
            ticker_array.append(i)
    print(ticker_array)
    return ticker_array


# gets earning report summary from earningswhispers.com
def get_earnings_report_xpath(TICKER, earning_quarter='4th'):
    try:
        tree = get_tree(f'https://www.earningswhispers.com/epsdetails/{TICKER}')
        release_Date = tree.xpath('//*[@id="chartbox"]/text()')[0]
        reported_Earnings = tree.xpath('//*[@id="surprise"]/div[4]/text()')[0].replace('$', '')
        consesus_Earnings = tree.xpath('//*[@id="surprise"]/div[10]/text()')[0].replace('$', '')
        reported_Revenues = tree.xpath('//*[@id="surprise"]/div[12]/text()')[0].replace('$', '').replace(' ', '').replace('il', '')
        consesus_Revenues = tree.xpath('//*[@id="surprise"]/div[14]/text()')[0].replace('$', '').replace(' ', '').replace('il', '')
        YoY = tree.xpath('//*[@id="qgrowth"]/div[5]/script/text()')[0]
        start = ', "'
        end = '%"'
        YoY = YoY[YoY.find(start)+len(start):YoY.rfind(end)] + str('%')
        report_summary = f'\nTICKER: {TICKER}\nRelease Date: {release_Date}\nEPS: {reported_Earnings} vs est {consesus_Earnings}\nRev: {reported_Revenues} vs est {consesus_Revenues}\nYoY: {YoY}\n'

        # remember each company have different year to year report, EX) apple's first quarter starts in Oct.
        if earning_quarter not in release_Date:
            report_summary = f'\nOnly have old reports for TICKER: {TICKER}\n'
        print(report_summary)
        return report_summary

    except:
        n_a = f'\nTICKER: {TICKER} is Not Available\n'
        print(n_a)
        return n_a


def get_earnings_report_soup(TICKER, earning_quarter='4th'):
    try:
        soup = get_soup(f'https://www.earningswhispers.com/epsdetails/{TICKER}')
        page = requests.get(f'https://www.earningswhispers.com/epsdetails/{TICKER}')
        tree = html.fromstring(page.content)

        release_Date = tree.xpath('//*[@id="chartbox"]/text()')
        if release_Date:
            release_Date = release_Date[0]

        reported_Earnings = soup.find("div", {"class": "mainitem"})
        if reported_Earnings:

            reported_Earnings = reported_Earnings.text.replace('$', '')
        else:
            reported_Earnings = 'N/A'

        consesus_Earnings = soup.find("div", {"class": "thirditem"})
        if consesus_Earnings:
            consesus_Earnings = consesus_Earnings.text.replace('$', '')
        else:
            consesus_Earnings = 'N/A'

        reported_Revenues = soup.find("div", {"class": "fourthitem"})
        if reported_Revenues:
            reported_Revenues = reported_Revenues.text.replace('$', '').replace(' ', '').replace('il', '')
        else:
            reported_Earnings = 'N/A'

        consesus_Revenues= soup.find("div", {"class": "fifthitem"})
        if consesus_Revenues:
            consesus_Revenues = consesus_Revenues.text.replace('$', '').replace(' ', '').replace('il', '')
        else:
            consesus_Revenues = 'N/A'

        YoY = soup.find("div", {"class": "revgrowth"})
        if YoY:
            YoY = YoY.text
            start = ', "'
            end = '%"'
            YoY = YoY[YoY.find(start) + len(start):YoY.rfind(end)] + str('%')

        else:
            YoY = 'N/A'

        report_summary = f'\nTICKER: {TICKER}\nRelease Date: {release_Date}\nEPS: {reported_Earnings} vs est {consesus_Earnings}\nRev: {reported_Revenues} vs est {consesus_Revenues}\nYoY: {YoY} \n'

        if earning_quarter not in release_Date:
            report_summary = f'\nOnly have old reports for TICKER: {TICKER}\n'
        print(report_summary)

        return report_summary

    except:
        n_a = f'\nTICKER: {TICKER} is Not Available\n'
        print(n_a)
        return n_a








# send email via gmail, remember to lower google account security to use this function
def send_email(to='', subject='Earnings Whispers', message=str('')):
    try:
        smtp = smtplib.SMTP('smtp.gmail.com', 587)
        smtp.ehlo()  # say Hello
        smtp.starttls()  # TLS 사용시 필요
        smtp.login(credential[0], credential[1])
        msg = MIMEText(message)
        msg['Subject'] = subject
        msg['To'] = to
        smtp.sendmail(credential[0], to, msg.as_string())
        smtp.quit()

        print(
            f'####Email Success####\n To: {to}\n Subject: {subject} \n Message: {message}'
        )
    except:
        print('Email Error')





if __name__ == "__main__":
    # gets tickers for specifc day
    ticker_array = get_earnings_list(date='2019-02-25')

    # brings reports into one string
    report_string = ''
    for i in ticker_array:
        report_string += get_earnings_report_soup(i)
    # send summary of earning reports via email if there is a report
    # put your email address here
    if report_string:
        send_email(to='ABC@gmail.com', message=report_string)

