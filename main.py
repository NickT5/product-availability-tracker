import json
from time import sleep
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException

from notify import Notify
from recipients import Recipients


def click_button(driver: webdriver.Chrome, query: str, find_by: str = "xpath", max_retries: int = 1) -> bool:
    """
    Click on a button using a query with a limited number of retries. The query can be of type xpath and class.
    :param driver: Chrome web browser
    :type driver: webdriver.Chrome
    :param query: the button to be searched for
    :type query: str
    :param find_by: the type of the query
    :type find_by: str
    :param max_retries: how many times it should try to find and click on the button
    :type max_retries: int
    :return: wether or not the button was clicked
    :rtype: bool
    """
    retries = 0
    is_clicked = False
    while not is_clicked and retries < max_retries:
        try:
            if find_by == "xpath": driver.find_element_by_xpath(query).click()
            elif find_by == "class": driver.find_element_by_class_name(query).click()
            else: NotImplemented
            is_clicked = True
        except NoSuchElementException:
            # print("NoSuchElementException")
            retries += 1
            sleep(1)
        except Exception as e:
            print(e)
    return is_clicked


def main():
    # create chrome web browser
    driver = webdriver.Chrome()

    # read products from inventory file
    products = []                  # which products to be searched for
    notified_max_counter: int = 0  # how many times a recipient will receive a notification when a product is available
    path = "C:/Users/nick/Documents/projects/product-availability-tracker/inventory.json"
    try:
        with open(path, 'r') as inventory_file:
            inventory = json.load(inventory_file)
            products = inventory["products"]
            notified_max_counter = inventory["notified_max_counter"]
    except FileNotFoundError:
        print(f"File not found: {path}. Failed to read products from inventory!")
        return

    # check if products are in stock/available
    for i, product in enumerate(products):
        driver.get(product["link"])

        # click on the accept cookies button
        click_button(driver, "//button[@type='submit' and @name='accept_cookie']", max_retries=1)

        # click on the add to shopping cart button
        is_clicked = click_button(driver, "js-add-to-cart-button", find_by="class", max_retries=2)
        if is_clicked:
            print(f"Product {product['name']} is available.")
            product["available"] = 1
            inventory["products"][i]["notified_counter"] += 1  # update inventory value
        else:
            print(f"Product {product['name']} is not available.")
            product["available"] = 0

    # update (counters from) products in inventory
    try:
        with open(path, 'w') as inventory_file:
            json.dump(inventory, inventory_file, indent=4)
    except FileNotFoundError:
        print(f"File not found: {path}. Failed to update inventory!")
        return

    # send notification (email, sms, ... ? ) with the available products to the recipients
    # build email
    email_content = [f"- {p['name']}: {p['link']}\n" for p in products if p["available"] == 1 and p["notified_counter"] < notified_max_counter]
    if len(email_content) <= 0:
        print("Not sending an email because there are no available products or the notified counter has been exceeded.")
    else:
        email_intro = f"Hi,\nThese products are available:" if len(email_content) > 1 else "Hi,\nThis product is available:"
        email_body = "%s \n %s \n\nGr,\nNick" % (email_intro, "".join(email_content))
        email_subject = "Products are available!" if len(email_content) > 1 else "Product is available!"

        # send email to recipients
        notifier = Notify()
        for recipient in Recipients.get_recipients():
            notifier.send_email(recipient=recipient, email_subject=email_subject, email_body=email_body)

    # close chrome browser
    if driver:
        driver.close()


if __name__ == "__main__":
    main()
