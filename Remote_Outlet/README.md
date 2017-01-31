# Remote-Outlet
RF Remote outlet based on [Etekcity Wireless Outlets](https://smile.amazon.com/Etekcity-Wireless-Electrical-Household-Appliances/dp/B00DQELHBS?ie=UTF8&keywords=power%20outlet%20rf&qid=1483998978&ref_=sr_1_1&sr=8-1) and [433Mhz RF module](https://smile.amazon.com/SMAKN-433Mhz-Transmitter-Receiver-Arduino/dp/B00M2CUALS/ref=pd_sbs_107_2?_encoding=UTF8&pd_rd_i=B00M2CUALS&pd_rd_r=R2FPYFDM5Q6123N14BFH&pd_rd_w=NQDSk&pd_rd_wg=ktDi6&psc=1&refRID=R2FPYFDM5Q6123N14BFH). Full on tutorial for setup [here] (https://www.samkear.com/hardware/control-power-outlets-wirelessly-raspberry-pi)

# Setup
1. Run the ansible raspi_setup with rf_devices.yml by modifying main.yml to install the necessary packages 
2. ssh onto the raspberry pi and run build on ~/WiringPi (This step could not be automated on ansible)
3. Setup the config.py file by getting the appropriate codes and pulses that you get from using /var/www/rfoutlet/RFSniffer
