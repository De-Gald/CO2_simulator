FROM mongo:latest

COPY . ./mongo_data
CMD mongoimport --host mongodb --jsonArray -d co2sim -c formations mongo_data/formations.json && \
    mongoimport --host mongodb --jsonArray -d co2sim -c formations_data mongo_data/formations_data.json
