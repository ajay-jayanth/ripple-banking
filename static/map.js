async function initMap() {
  // Use the global variables defined in the HTML
  const map = new google.maps.Map(document.querySelector('.map-placeholder'), {
      center: { lat: CUSTOMER_LAT, lng: CUSTOMER_LNG },
      zoom: 14,
      mapId: 'DEMO_MAP_ID'
  });

  // Add customer marker (blue)
  const customerMarker = new google.maps.Marker({
      position: { lat: CUSTOMER_LAT, lng: CUSTOMER_LNG },
      map: map,
      icon: {
          url: 'https://maps.google.com/mapfiles/ms/icons/blue-dot.png',
          scaledSize: new google.maps.Size(40, 40)
      },
      title: 'Your Location',
      zIndex: 1000
  });

  const customerInfo = new google.maps.InfoWindow({
      content: `
          <div style="color: #1a1a2e; padding: 10px;">
              <strong>Your Location</strong><br>
              ${CUSTOMER_ADDRESS}
          </div>
      `,
      ariaLabel: "Your Location",
  });

  customerMarker.addListener('click', () => {
      customerInfo.open({
          anchor: customerMarker,
          map
      });
  });

  // Process merchant data
  const merchants = JSON.parse(document.getElementById('merchant-data').textContent);
  const bounds = new google.maps.LatLngBounds();
  bounds.extend({ lat: CUSTOMER_LAT, lng: CUSTOMER_LNG });

  merchants.forEach(merchant => {
      const lat = parseFloat(merchant.latitude);
      const lng = parseFloat(merchant.longitude);

      if (isNaN(lat) || isNaN(lng)) return;

      const position = { lat, lng };

      const marker = new google.maps.Marker({
          position: position,
          map: map,
          icon: {
              url: 'https://maps.google.com/mapfiles/ms/icons/green-dot.png',
              scaledSize: new google.maps.Size(35, 35)
          },
          title: merchant.name
      });

      const merchantInfo = new google.maps.InfoWindow({
          content: `
              <div style="color: #1a1a2e; padding: 10px;">
                  <strong>${merchant.name}</strong><br>
                  ${merchant.address}<br>
                  ${merchant.stars ? `Rating: ${merchant.stars}<br>` : ''}
                  ${merchant.business_hours || 'Hours not available'}
              </div>
          `
      });

      marker.addListener('click', () => {
          merchantInfo.open({
              anchor: marker,
              map
          });
      });

      bounds.extend(position);
  });

  // Fit map to show all markers
  if (!bounds.isEmpty()) {
      map.fitBounds(bounds, { padding: 50 });
  }

  const sortDistanceButton = document.getElementById('sort-distance-button');
    const sortRatingButton = document.getElementById('sort-rating-button');
    let sortAscending = true;

    sortDistanceButton.addEventListener('click', () => {
        // Sort the merchants array based on distance
        merchants.sort((a, b) => {
            return sortAscending ? a.distance - b.distance : b.distance - a.distance;
        });
    
        // Get the parent element of the merchant cards
        const merchantsList = document.querySelector('.merchants-list');
    
        // Create an array of merchant card elements
        const merchantCards = Array.from(merchantsList.querySelectorAll('.merchant-card'));
    
        // Rearrange the cards based on the sorted merchants array
        merchants.forEach(merchant => {
            const card = merchantCards.find(
                card => card.getAttribute('data-name') === merchant.name
            );
            if (card) {
                merchantsList.appendChild(card); // Move the card to the end of the list
            }
        });
    
        // Toggle the sorting order
        sortAscending = !sortAscending;
    });
    


    sortRatingButton.addEventListener('click', () => {
        // Sort the merchants array based on rating
        merchants.sort((a, b) => {
            if (sortAscending) {
                return b.rating - a.rating;
            } else {
                return a.rating - b.rating;
            }
        });

        // Get the parent element of the merchant cards
        const merchantsList = document.querySelector('.merchants-list');
    
        // Create an array of merchant card elements
        const merchantCards = Array.from(merchantsList.querySelectorAll('.merchant-card'));
    
        // Rearrange the cards based on the sorted merchants array
        merchants.forEach(merchant => {
            const card = merchantCards.find(
                card => card.getAttribute('data-name') === merchant.name
            );
            if (card) {
                merchantsList.appendChild(card); // Move the card to the end of the list
            }
        });
    
        // Toggle the sorting order
        sortAscending = !sortAscending;
    });

}

window.initMap = initMap;