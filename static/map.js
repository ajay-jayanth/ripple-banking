async function initMap() {
    // Styles a map in night mode.
    const { AdvancedMarkerElement } = await google.maps.importLibrary("marker");

    const map = new google.maps.Map(document.querySelector(".map-placeholder"), {
      center: { lat: customerLat, lng: customerLong },
      zoom: 12,
      styles: [
        { elementType: "geometry", stylers: [{ color: "#242f3e" }] },
        { elementType: "labels.text.stroke", stylers: [{ color: "#242f3e" }] },
        { elementType: "labels.text.fill", stylers: [{ color: "#746855" }] },
        {
          featureType: "administrative.locality",
          elementType: "labels.text.fill",
          stylers: [{ color: "#d59563" }],
        },
        {
          featureType: "poi",
          elementType: "labels.text.fill",
          stylers: [{ color: "#d59563" }],
        },
        {
          featureType: "poi.park",
          elementType: "geometry",
          stylers: [{ color: "#263c3f" }],
        },
        {
          featureType: "poi.park",
          elementType: "labels.text.fill",
          stylers: [{ color: "#6b9a76" }],
        },
        {
          featureType: "road",
          elementType: "geometry",
          stylers: [{ color: "#38414e" }],
        },
        {
          featureType: "road",
          elementType: "geometry.stroke",
          stylers: [{ color: "#212a37" }],
        },
        {
          featureType: "road",
          elementType: "labels.text.fill",
          stylers: [{ color: "#9ca5b3" }],
        },
        {
          featureType: "road.highway",
          elementType: "geometry",
          stylers: [{ color: "#746855" }],
        },
        {
          featureType: "road.highway",
          elementType: "geometry.stroke",
          stylers: [{ color: "#1f2835" }],
        },
        {
          featureType: "road.highway",
          elementType: "labels.text.fill",
          stylers: [{ color: "#f3d19c" }],
        },
        {
          featureType: "transit",
          elementType: "geometry",
          stylers: [{ color: "#2f3948" }],
        },
        {
          featureType: "transit.station",
          elementType: "labels.text.fill",
          stylers: [{ color: "#d59563" }],
        },
        {
          featureType: "water",
          elementType: "geometry",
          stylers: [{ color: "#17263c" }],
        },
        {
          featureType: "water",
          elementType: "labels.text.fill",
          stylers: [{ color: "#515c6d" }],
        },
        {
          featureType: "water",
          elementType: "labels.text.stroke",
          stylers: [{ color: "#17263c" }],
        },
      ],
      mapId: "4504f8b37365c3d0",
    });

    merchantList.forEach(merchant => {
        const marker = new AdvancedMarkerElement({
            map,
            position: { lat: merchant['latitude'], lng: merchant['longitude'] },
        });
        
    })
  }
  
window.initMap = initMap;
  

// async function initMap() {
//     const contentString = `
//       <div>
//         <h1>Uluru</h1>
//         <div>
//           <p>
//             <b>Uluru</b>, also referred to as <b>Ayers Rock</b>, is a large
//             sandstone rock formation in the southern part of the
//             Northern Territory, central Australia. It lies 335&#160;km (208&#160;mi)
//             south west of the nearest large town, Alice Springs; 450&#160;km
//             (280&#160;mi) by road. Kata Tjuta and Uluru are the two major
//             features of the Uluru - Kata Tjuta National Park. Uluru is
//             sacred to the Pitjantjatjara and Yankunytjatjara, the
//             Aboriginal people of the area. It has many springs, waterholes,
//             rock caves and ancient paintings. Uluru is listed as a World
//             Heritage Site.
//           </p>
//           <p>
//             Attribution: Uluru,
//             <a href="https://en.wikipedia.org/w/index.php?title=Uluru&oldid=297882194">
//               https://en.wikipedia.org/w/index.php?title=Uluru
//             </a>
//             (last visited June 22, 2009).
//           </p>
//         </div>
//       </div>`;
//     const infoWindow = new google.maps.InfoWindow({
//         content: contentString,
//         ariaLabel: "Uluru",
//     });

//     const marker = document.querySelector('gmp-advanced-marker');
//     marker.addEventListener('gmp-click', () => {
//         infoWindow.open({anchor: marker});
//     });
// }

//   window.initMap = initMap;