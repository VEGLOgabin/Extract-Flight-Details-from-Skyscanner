import asyncio
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup
import csv
import time
async def scrape_flight_details_from_skyscanner():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)  # Set headless=True if you do not need to see the browser
        page = await browser.new_page()

        # Go to the Bing News search page
        await page.goto('https://www.skyscanner.net/transport/flights/cooa/nbo/240902/240909/?adultsv2=1&cabinclass=economy&childrenv2=&ref=home&rtn=1&preferdirects=false&outboundaltsenabled=false&inboundaltsenabled=false', timeout=600000)

        data = []
        base_url = "https://www.skyscanner.net"
        

        up = True
        while up:
            await page.wait_for_timeout(5000)  # Here is a timeout  for the new content to load
            
            # Extract content
            content = await page.content()
            soup = BeautifulSoup(content, 'lxml')
            
            # Find all flight options
            flights = soup.find_all('a', class_='FlightsTicket_link__OWUzM')

            for flight in flights:
                # Extract airline name
                airline_name = flight.find('span', class_='BpkText_bpk-text--xs__MWRhZ')
                airline_name = airline_name.text.strip() if airline_name else 'N/A'

                # Extract flight details using screen reader elements
                flight_info = flight.find('div', class_='UpperTicketBody_screenReaderOnly__ZTJmN')
                if flight_info:
                    details = flight_info.text.strip().split('.')

                    outbound_details = details[1].split(',')
                    inbound_details = details[4].split(',')

                    outbound_airlines = outbound_details[0].replace('Outbound flight with', '').strip()
                    outbound_departure = outbound_details[1].replace('Departing from', '').strip()
                    outbound_arrival = outbound_details[2].replace('arriving in', '').strip()

                    inbound_airlines = inbound_details[0].replace('Inbound flight with', '').strip()
                    inbound_departure = inbound_details[1].replace('Departing from', '').strip()
                    inbound_arrival = inbound_details[2].replace('arriving in', '').strip()

                else:
                    outbound_airlines = outbound_departure = outbound_arrival = inbound_airlines = inbound_departure = inbound_arrival = 'N/A'

                # Extract price
                flight_price = flight.find('span', class_='BpkText_bpk-text--lg__ZTY1M')
                flight_price = flight_price.text.strip() if flight_price else 'N/A'

                # Print or store the scraped data
                print(f"Airline: {airline_name}")
                print(f"Outbound Airlines: {outbound_airlines}")
                print(f"Outbound Departure: {outbound_departure}")
                print(f"Outbound Arrival: {outbound_arrival}")
                print(f"Inbound Airlines: {inbound_airlines}")
                print(f"Inbound Departure: {inbound_departure}")
                print(f"Inbound Arrival: {inbound_arrival}")
                print(f"Price: {flight_price}")
                print()

                # Store data
                data.append({
                    'Airline': airline_name,
                    'Outbound Airlines': outbound_airlines,
                    'Outbound Departure': outbound_departure,
                    'Outbound Arrival': outbound_arrival,
                    'Inbound Airlines': inbound_airlines,
                    'Inbound Departure': inbound_departure,
                    'Inbound Arrival': inbound_arrival,
                    'Price': flight_price
                })
                
            up = False

        # Save data to CSV
        if len(data) > 0:
            with open('flights_from_skyscanner.csv', 'w', newline='', encoding='utf-8') as csvfile:
                fieldnames = ['Airline', 'Outbound Airlines', 'Outbound Departure', 'Outbound Arrival', 'Inbound Airlines', 'Inbound Departure', 'Inbound Arrival', 'Price']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                for row in data:
                    writer.writerow(row)

            print(f'Scraped {len(data)} flights. Data saved to flights_from_skyscanner.csv.')

        else:
            print(f'Scraped {len(data)} flights.')



        # Close the browser
        await browser.close()

# Run the scrape function
asyncio.run(scrape_flight_details_from_skyscanner())





