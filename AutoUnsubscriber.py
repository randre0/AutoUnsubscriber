import imapclient, pyzmail, imaplib, bs4, webbrowser, getpass


def connect_mail(email, password):
    provider = email.split('@', 1)[1]
    print(provider)
    if provider == "gmail.com":
        imap_server = "imap.gmail.com"
    elif provider == "hotmail.com" or provider == "outlook.com":
        imap_server = "imap-mail.outlook.com"
    elif provider == "yahoo.com" or provider == "ymail.com":
        imap_server = "imap.mail.yahoo.com"

    imap_obj = imapclient.IMAPClient(imap_server, ssl=True)
    print(imap_obj.login(email, password))
    imap_obj.select_folder('[Gmail]/Starred', readonly=False)
    UIDs = imap_obj.search('ALL')
    return imap_obj, UIDs


def read_messages(imap_obj, UIDs):
    senders = dict()
    raw_messages = imap_obj.fetch(UIDs, ['BODY[]'])
    for x in range(0, len(UIDs)):
        message = pyzmail.PyzMessage.factory(raw_messages[UIDs[x]][b'BODY[]'])
        try:
            if message.html_part != None and message.html_part.charset != None:
                text = message.html_part.get_payload().decode(message.html_part.charset)
                bs4_object = bs4.BeautifulSoup(text, "html.parser")
                elems = bs4_object.select('a')
                for i in range(0, len(elems)):
                    text = elems[i].getText()
                    if "Unsubscribe" in text:
                        sender = message.get_addresses('from')[0]
                        if sender not in senders:
                            senders[sender] = [[UIDs[x]], elems[i].get('href')]
                        else:
                            senders[sender][0].append(UIDs[x])
        except UnicodeDecodeError:
            continue
    return senders


def unsubscribe(senders, imap_obj):
    for k, v in senders.items():
        prompt = input('Would you like to unsubscribe from ' + k[0] + '? [Y or N] \n')
        if prompt == 'Y' or prompt == 'y':
            prompt2 = input('Would you like to delete emails from ' + k[0] + 'as well? [Y or N] \n')
            webbrowser.open(v[1])
            if prompt2 == 'Y' or prompt2 == 'y':
                imap_obj.delete_messages(v[0])
                imap_obj.expunge()

    imap_obj.logout()


if __name__ == '__main__':
    imaplib._MAXLINE = 10000000
    email = input("Enter email address:")
    email = email.strip()
    password = input("Enter Password:")
    password = password.strip()
    imap_obj, UIDs = connect_mail(email, password)
    senders = read_messages(imap_obj, UIDs)
    unsubscribe(senders, imap_obj)
