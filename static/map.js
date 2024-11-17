async function initMap() {
  const map = new google.maps.Map(document.querySelector('.map-placeholder'), {
      center: { lat: CUSTOMER_LAT, lng: CUSTOMER_LNG },
      zoom: 14,
      mapId: 'DEMO_MAP_ID'
  });

  function createRippleEffect(position) {
      const rippleDiv = document.createElement('div');
      rippleDiv.className = 'ripple-container';
      rippleDiv.style.cssText = `
          position: absolute;
          pointer-events: none;
          width: 100px;
          height: 100px;
          transform: translate(-50%, -50%);
      `;

      for (let i = 0; i < 3; i++) {
          const ripple = document.createElement('div');
          ripple.className = 'ripple';
          ripple.style.cssText = `
              position: absolute;
              width: 100%;
              height: 100%;
              border-radius: 50%;
              border: 2px solid #4ecca3;
              opacity: 0;
          `;
          rippleDiv.appendChild(ripple);
      }

      if (!document.querySelector('#ripple-styles')) {
          const style = document.createElement('style');
          style.id = 'ripple-styles';
          style.textContent = `
              .ripple {
                  animation: rippleEffect 2s ease-out forwards;
              }
              @keyframes rippleEffect {
                  0% {
                      transform: scale(0);
                      opacity: 1;
                  }
                  100% {
                      transform: scale(1);
                      opacity: 0;
                  }
              }
          `;
          document.head.appendChild(style);
      }

      rippleDiv.querySelectorAll('.ripple').forEach((ripple, index) => {
          ripple.style.animationDelay = `${index * 0.3}s`;
      });

      const overlay = new google.maps.OverlayView();
      overlay.onAdd = function() {
          this.getPanes().overlayLayer.appendChild(rippleDiv);
      };
      
      overlay.draw = function() {
          const projection = this.getProjection();
          const point = projection.fromLatLngToDivPixel(position);
          rippleDiv.style.left = point.x + 'px';
          rippleDiv.style.top = point.y + 'px';
      };

      overlay.setMap(map);

      setTimeout(() => {
          rippleDiv.remove();
          overlay.setMap(null);
      }, 2000);
  }

  const frogMarker = new google.maps.Marker({
      position: { lat: CUSTOMER_LAT, lng: CUSTOMER_LNG },
      map: map,
      icon: {
          url: '/static/images/frog.png',
          scaledSize: new google.maps.Size(43*1.5, 35*1.5),
          anchor: new google.maps.Point(30, 30)
      },
      optimized: false,
      zIndex: 1001
  });

  const customerMarker = new google.maps.Marker({
      position: { lat: CUSTOMER_LAT, lng: CUSTOMER_LNG },
      map: map,
      icon: {
          url: 'https://maps.google.com/mapfiles/ms/icons/red-dot.png',
          scaledSize: new google.maps.Size(60, 60)
      },
      title: 'Your Location',
      zIndex: 1000
  });

  let currentInfoWindow = null;
  let currentRippleOverlay = null;
  let lastClickedPosition = { lat: CUSTOMER_LAT, lng: CUSTOMER_LNG };
  let activeCard = null;
  let activeMarker = null;
  let sortAscending = true;
  const markers = new Map();

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
      if (currentInfoWindow) {
          currentInfoWindow.close();
      }
      customerInfo.open({
          anchor: customerMarker,
          map
      });
      currentInfoWindow = customerInfo;
  });

  function animateFrog() {
      const bounce = [
          { transform: 'translateY(0px)' },
          { transform: 'translateY(-20px)' },
          { transform: 'translateY(0px)' }
      ];
      
      const timing = {
          duration: 500,
          iterations: 1
      };

      if (frogMarker.getIcon().url) {
          const markerElement = frogMarker.getIcon().url;
          markerElement.animate(bounce, timing);
      }
  }

  function animateFrogJump(start, end, callback) {
      const frames = 50;
      const duration = 1000;
      let frame = 0;

      if (currentRippleOverlay) {
          currentRippleOverlay.setMap(null);
          currentRippleOverlay = null;
      }

      function calculateArcPoint(start, end, frame, frames) {
          const progress = frame / frames;
          const lat = start.lat + (end.lat - start.lat) * progress;
          const lng = start.lng + (end.lng - start.lng) * progress;
          const height = Math.sin(progress * Math.PI) * 0.0005;
          
          return {
              lat: lat + height,
              lng: lng
          };
      }

      const timer = setInterval(() => {
          frame++;
          
          if (frame <= frames) {
              const position = calculateArcPoint(start, end, frame, frames);
              frogMarker.setPosition(position);
              
              if (frame === Math.floor(frames / 2)) {
                  animateFrog();
              }
          } else {
              clearInterval(timer);
              createRippleEffect(end);
              if (callback) callback();
          }
      }, duration / frames);
  }

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
              url: 'https://maps.google.com/mapfiles/ms/icons/blue-dot.png',
              scaledSize: new google.maps.Size(60, 60)
          },
          title: merchant.name
      });

      markers.set(merchant.name, marker);

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
          if (currentInfoWindow) {
              currentInfoWindow.close();
          }
          
          merchantInfo.open({
              anchor: marker,
              map
          });
          currentInfoWindow = merchantInfo;
          
          if (activeCard) {
              activeCard.style.background = 'rgba(255, 255, 255, 0.1)';
          }
          
          const correspondingCard = document.querySelector(`.merchant-card[data-name="${merchant.name}"]`);
          if (correspondingCard) {
              correspondingCard.style.background = 'rgba(78, 204, 163, 0.2)';
              correspondingCard.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
              activeCard = correspondingCard;
          }
          
          animateFrogJump(lastClickedPosition, position, () => {
              lastClickedPosition = position;
          });
          
          activeMarker = marker;
      });

      bounds.extend(position);
  });

  document.querySelectorAll('.merchant-card').forEach(card => {
      card.addEventListener('click', () => {
          const lat = parseFloat(card.getAttribute('data-lat'));
          const lng = parseFloat(card.getAttribute('data-lng'));
          const merchantName = card.getAttribute('data-name');
          
          if (!isNaN(lat) && !isNaN(lng)) {
              const position = { lat, lng };
              
              if (activeCard) {
                  activeCard.style.background = 'rgba(255, 255, 255, 0.1)';
              }
              
              card.style.background = 'rgba(78, 204, 163, 0.2)';
              activeCard = card;
              
              const marker = markers.get(merchantName);
              if (marker) {
                  google.maps.event.trigger(marker, 'click');
              }
              
              map.panTo(position);
              
              animateFrogJump(lastClickedPosition, position, () => {
                  lastClickedPosition = position;
              });
          }
      });
  });

  // Update sort buttons HTML
  document.querySelector('.sort-buttons').innerHTML = `
      <button id="sort-distance-button">Sort by Distance ↑</button>
      <button id="sort-rating-button">Sort by Rating ↑</button>
  `;

  // Sort by distance
  document.getElementById('sort-distance-button').addEventListener('click', () => {
      const merchantsList = document.querySelector('.merchants-list');
      const cards = Array.from(merchantsList.querySelectorAll('.merchant-card'));
      const sortedCards = cards.sort((a, b) => {
          const distanceA = parseFloat(a.querySelector('.merchant-details').textContent.match(/(\d+\.?\d*) miles/)[1]);
          const distanceB = parseFloat(b.querySelector('.merchant-details').textContent.match(/(\d+\.?\d*) miles/)[1]);
          return sortAscending ? distanceA - distanceB : distanceB - distanceA;
      });

      cards.forEach(card => card.remove());
      sortedCards.forEach(card => merchantsList.appendChild(card));
      
      sortAscending = !sortAscending;
      document.getElementById('sort-distance-button').textContent = 
          `Sort by Distance ${sortAscending ? '↑' : '↓'}`;
  });

  // Replace the rating sort event listener with this corrected version:

document.getElementById('sort-rating-button').addEventListener('click', () => {
  const merchantsList = document.querySelector('.merchants-list');
  const cards = Array.from(merchantsList.querySelectorAll('.merchant-card'));
  const sortedCards = cards.sort((a, b) => {
      // Get the entire rating text content
      const ratingTextA = a.querySelector('.merchant-rating').textContent.trim();
      const ratingTextB = b.querySelector('.merchant-rating').textContent.trim();
      
      // Parse the first number that appears (the stars rating)
      const ratingA = parseFloat(ratingTextA.match(/\d+\.?\d*/)?.[0]) || 0;
      const ratingB = parseFloat(ratingTextB.match(/\d+\.?\d*/)?.[0]) || 0;
      
      // Sort in descending order for ratings (higher ratings first)
      return sortAscending ? ratingB - ratingA : ratingA - ratingB;
  });

  // Clear existing cards
  cards.forEach(card => card.remove());

  // Append sorted cards
  sortedCards.forEach(card => merchantsList.appendChild(card));
  
  // Toggle sort direction
  sortAscending = !sortAscending;

  // Update button text
  document.getElementById('sort-rating-button').textContent = 
      `Sort by Rating ${sortAscending ? '↑' : '↓'}`;
});
  if (!bounds.isEmpty()) {
      map.fitBounds(bounds, { padding: 50 });
  }
}

window.initMap = initMap;