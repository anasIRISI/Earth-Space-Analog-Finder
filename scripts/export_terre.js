// ============================================================
//  Earth-Space Analog Finder : statistiques par cellule de 1°
// ============================================================
var CELL = 1;                                  // doit rester égal à CELL dans import_terre.py
var A0 = '2021-01-01', A1 = '2022-01-01';      // année de référence

// ---------- BLOCS : [lonMin, latMin, lonMax, latMax] ----------
var BLOCS = [
  // Analogues connus
  {nom: 'atacama',    b: [-72, -30, -66, -18]},
  {nom: 'mojave',     b: [-118, 34, -114, 38]},
  {nom: 'utah',       b: [-112, 37, -108, 40]},
  {nom: 'namib',      b: [12, -28, 17, -22]},
  {nom: 'lut',        b: [57, 28, 61, 32]},
  {nom: 'danakil',    b: [39, 12, 42, 15]},
  {nom: 'riotinto',   b: [-8, 36, -5, 39]},
  {nom: 'islande',    b: [-20, 63, -13, 66]},
  {nom: 'haughton',   b: [-92, 74, -86, 77]},
  {nom: 'antarctique',b: [158, -79, 164, -76]},
  // Contre-exemples (ne doivent PAS bien se classer)
  {nom: 'alpes',      b: [10, 44, 16, 48]},
  {nom: 'karakoram',  b: [70, 28, 80, 36]},
  {nom: 'plaines_us', b: [-100, 35, -90, 45]},
  {nom: 'congo',      b: [20, -5, 30, 5]}
];

// ---------- COUCHES ----------
// Relief : Copernicus GLO-30 (couverture mondiale), ramené à ~500 m (proche de MOLA)
var glo = ee.ImageCollection('COPERNICUS/DEM/GLO30');
var proj = glo.first().select('DEM').projection();
var elev = glo.select('DEM').mosaic().setDefaultProjection(proj)
  .reduceResolution({reducer: ee.Reducer.mean(), maxPixels: 1024})
  .reproject({crs: 'EPSG:4326', scale: 500}).rename('altitude');

var pente    = ee.Terrain.slope(elev).rename('pente');
var rugosite = elev.reduceNeighborhood({
  reducer: ee.Reducer.stdDev(), kernel: ee.Kernel.square(1)}).rename('rugosite');
var relief   = elev.focalMax(3).subtract(elev.focalMin(3)).rename('relief');
var valide   = elev.mask().rename('valide');           // 1 = donnée valide

// Albédo MODIS (moyenne annuelle)
var albedo = ee.ImageCollection('MODIS/061/MCD43A3').filterDate(A0, A1)
  .select('Albedo_WSA_shortwave').mean().multiply(0.001).rename('albedo');

// Température de surface MODIS : amplitude jour - nuit (K)
var lst = ee.ImageCollection('MODIS/061/MOD11A2').filterDate(A0, A1);
var jour = lst.select('LST_Day_1km').mean().multiply(0.02);
var nuit = lst.select('LST_Night_1km').mean().multiply(0.02);
var amplitude = jour.subtract(nuit).rename('amplitude');
amplitude = amplitude.updateMask(amplitude.gt(1));

// Inertie thermique apparente : 100 * (1 - albédo) / amplitude
var ati = ee.Image(1).subtract(albedo).divide(amplitude).multiply(100).rename('ati');

// Végétation (pour exclure les zones vertes)
var ndvi = ee.ImageCollection('MODIS/061/MOD13A2').filterDate(A0, A1)
  .select('NDVI').mean().multiply(0.0001).rename('ndvi');

// Aridité = précipitations / évapotranspiration potentielle (bas = aride)
var tc = ee.ImageCollection('IDAHO_EPSCOR/TERRACLIMATE')
  .filterDate('2020-01-01', '2021-01-01');
var aridite = tc.select('pr').sum()
  .divide(tc.select('pet').sum().multiply(0.1)).rename('aridite');

var image = ee.Image.cat([elev, pente, rugosite, relief, albedo,
                          amplitude, ati, ndvi, aridite, valide]);

// Statistiques : moyenne, écart-type, percentile 90
var reducer = ee.Reducer.mean()
  .combine({reducer2: ee.Reducer.stdDev(), sharedInputs: true})
  .combine({reducer2: ee.Reducer.percentile([90]), sharedInputs: true});

// ---------- CELLULES ----------
function cellules(b) {
  var lons = ee.List.sequence(b[0], b[2] - CELL, CELL);
  var lats = ee.List.sequence(b[1], b[3] - CELL, CELL);
  var liste = lons.map(function (x) {
    return lats.map(function (y) {
      var lon = ee.Number(x), lat = ee.Number(y);
      return ee.Feature(
        ee.Geometry.Rectangle([lon, lat, lon.add(CELL), lat.add(CELL)], 'EPSG:4326', false),
        {lon0: lon, lat0: lat});
    });
  });
  return ee.FeatureCollection(ee.List(liste).flatten());
}

// ---------- EXPORT ----------
var COLONNES = ['lon0', 'lat0', 'altitude_mean', 'pente_mean', 'pente_stdDev',
  'pente_p90', 'rugosite_mean', 'rugosite_stdDev', 'relief_mean', 'albedo_mean',
  'albedo_stdDev', 'amplitude_mean', 'ati_mean', 'ndvi_mean', 'aridite_mean',
  'valide_mean'];

BLOCS.forEach(function (bloc, i) {
  var res = image.reduceRegions({
    collection: cellules(bloc.b), reducer: reducer, scale: 500, tileScale: 4
  }).filter(ee.Filter.gt('valide_mean', 0.5));         // enlève océans et trous

  print('Cellules gardées – ' + bloc.nom, res.size());
  if (i === 0) {                                       // aperçu du premier bloc
    print('Exemple :', res.first());
    Map.centerObject(res, 5);
    Map.addLayer(res, {}, 'cellules');
  }
  Export.table.toDrive({
    collection: res,
    description: 'terre_' + bloc.nom,
    folder: 'GEE_terre',
    fileFormat: 'CSV',
    selectors: COLONNES
  });
});