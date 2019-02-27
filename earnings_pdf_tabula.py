from tabula import read_pdf
import smtplib
from email.mime.text import MIMEText
from PRIVATE_INFO import credential


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





def get_charts_from_pdf(file, page_number=['6']):
    report_string = ''
    df = read_pdf(file, multiple_tables=True, pages=page_number)
    print(df.to_string())
    for index, row in df.iterrows():
        if '$' in row[2]:

            reported_EPS = float(str(row[2]).replace('$', '').replace(',', ''))
            est_EPS = float(str(row[3]).replace('$', '').replace(',', ''))
            reported_revenue = float(str(row[4]).replace('$', '').replace(',', ''))
            est_revenue = float(str(row[4]).replace('$', '').replace(',', ''))
            if reported_revenue > 1000:
                reported_revenue = str(round(reported_revenue/1000, 2)) + 'B'
            else:
                reported_revenue = str(reported_revenue) + 'M'

            if est_revenue > 1000:
                est_revenue = str(round(est_revenue / 1000, 2)) + 'B'
            else:
                est_revenue = str(est_revenue) + 'M'


            report_summary = f'\nTICKER: {row[0]}\nEPS: {reported_EPS} vs est {est_EPS}\nRev: {reported_revenue} vs est {est_revenue}\nYoY: {row[6]}'
            if type(row[7]) == str:
                side_note = row[7]
                report_summary += f'\n{side_note}'
            else:
                report_summary += f'\n'

            report_string = report_string + '\n' + report_summary
            print(report_string)


    return report_string, page_number


if __name__ == "__main__":
    report_string, page_number = get_charts_from_pdf('YOUR_PDF_FILE')
