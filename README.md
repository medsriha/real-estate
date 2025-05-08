# React Google Maps Example

A simple React application that displays a Google Map using the [@vis.gl/react-google-maps](https://github.com/visgl/react-google-maps) library.

## Setup

1. Replace `YOUR_API_KEY` in both `App.js` and `AdvancedExample.js` with your actual Google Maps API key.
2. Install dependencies:
   ```
   npm install
   ```
3. Start the development server:
   ```
   npm start
   ```

## Examples

This project includes two examples:

### Basic Example (App.js)
- Displays a Google Map centered on New York City
- Adds a marker at the centered location using the AdvancedMarker component
- Responsive design
- Uses the official @vis.gl/react-google-maps library

### Advanced Example (AdvancedExample.js)
- Multiple custom styled markers
- Interactive InfoWindows that open on marker click
- Geocoding functionality with address search
- Map centering and zoom controls

To switch between examples, edit the `index.js` file and uncomment the desired component:

```jsx
<React.StrictMode>
  {/* Basic example */}
  <App />
  
  {/* Advanced example - uncomment to use */}
  {/* <AdvancedExample /> */}
</React.StrictMode>
```

## Customization

To change the map location, modify the `position` object in the components:

```javascript
const position = { lat: YOUR_LATITUDE, lng: YOUR_LONGITUDE };
```

You can also adjust the zoom level, map ID, and other map options as supported by the `Map` component from @vis.gl/react-google-maps.

## Additional Features

The @vis.gl/react-google-maps library offers many more components and hooks:

- Various marker types (Marker, AdvancedMarker)
- InfoWindow component
- Libraries for routing, geocoding, places, and more
- Access to additional Maps JavaScript API features

Check out the [official documentation](https://visgl.github.io/react-google-maps) for more details.