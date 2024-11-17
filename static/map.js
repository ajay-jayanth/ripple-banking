async function initMap() {
  const map = new google.maps.Map(document.querySelector('.map-placeholder'), {
      center: { lat: CUSTOMER_LAT, lng: CUSTOMER_LNG },
      zoom: 14,
      mapId: 'DEMO_MAP_ID'
  });

  // Create ripple effect overlay
  // Modify createRippleEffect function to return the overlay
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

    // Create three ripple circles
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

    // Add styles if not already present
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

    // Trigger animations with slight delays
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

    // Completely remove the overlay and its contents after 2 seconds
    setTimeout(() => {
        rippleDiv.remove();  // Remove the div from the DOM
        overlay.setMap(null); // Remove the overlay from the map
    }, 2000);
}


  // Create the frog marker
  const frogMarker = new google.maps.Marker({
      position: { lat: CUSTOMER_LAT, lng: CUSTOMER_LNG },
      map: map,
      icon: {
          url: '/static/images/frog.png',
          scaledSize: new google.maps.Size(43*1.5, 35*1.5),
          anchor: new google.maps.Point(30, 30)
      },
      style: {
        overflow: 'hidden'
      },
      optimized: false,
      zIndex: 1001
  });

  // Add customer marker (red pin)
  const customerMarker = new google.maps.Marker({
      position: { lat: CUSTOMER_LAT, lng: CUSTOMER_LNG },
      map: map,
      icon: {
          url: 'https://maps.google.com/mapfiles/ms/icons/red-dot.png',
          scaledSize: new google.maps.Size(60, 60)  // Larger pin
      },
      title: 'Your Location',
      zIndex: 1000
  });

  let currentInfoWindow = null;
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

  // Process merchant data
  const merchants = JSON.parse(document.getElementById('merchant-data').textContent);
  const bounds = new google.maps.LatLngBounds();
  bounds.extend({ lat: CUSTOMER_LAT, lng: CUSTOMER_LNG });

  let lastClickedPosition = { lat: CUSTOMER_LAT, lng: CUSTOMER_LNG };
  let activeCard = null;
  let activeMarker = null;
  const markers = new Map();

  let currentRippleOverlay = null;  // Add this at the top with other variables

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

  // Clear any existing ripple when starting a new jump
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
          // Create new ripple effect and store its reference
          currentRippleOverlay = createRippleEffect(end);
          if (callback) callback();
      }
  }, duration / frames);
}

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
              scaledSize: new google.maps.Size(60, 60)  // Larger pin
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

  // Click listener for merchant cards
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

  if (!bounds.isEmpty()) {
      map.fitBounds(bounds, { padding: 50 });
  }
}

window.initMap = initMap;