CREATE EXTENSION IF NOT EXISTS postgis;

-- This spatial reference system is used for everything
INSERT INTO spatial_ref_sys (srid, auth_name, auth_srid, srtext, proj4text) VALUES (
  900914,
  'IAU',
  900914,
  'GEOGCS["GCS_Mars_2000_Sphere",DATUM["Mars_2000_(Sphere)",SPHEROID["Mars_2000_Sphere_IAU_IAG",3396190,0],AUTHORITY["ESRI","106971"]],PRIMEM["Reference_Meridian",0],UNIT["Degree",0.0174532925199433],AXIS["Longitude",EAST],AXIS["Latitude",NORTH]]")',
  '+proj=longlat +R=3396190 +no_defs'
) ON CONFLICT DO NOTHING;

-- Table that matches the layout of PDS coverage shapefiles
CREATE TABLE IF NOT EXISTS footprints (
    ogc_fid SERIAL PRIMARY KEY,
    centerlat numeric(10,6),
    centerlon numeric(10,6),
    maxlat numeric(10,6),
    minlat numeric(10,6),
    eastlon numeric(10,6),
    westlon numeric(10,6),
    emangle numeric(10,6),
    inangle numeric(10,6),
    phangle numeric(10,6),
    sollong numeric(10,6),
    npolestate character varying(1),
    spolestate character varying(1),
    target character varying(10),
    productid character varying(100) UNIQUE,
    datasetid character varying(100),
    insthostid character varying(15),
    instid character varying(15),
    utcstart character varying(23),
    utcend character varying(23),
    pdsvolid character varying(25),
    prodtype character varying(40),
    createdate character varying(23),
    shpsource character varying(100),
    exturl character varying(254),
    ext2url character varying(254),
    ext3url character varying(254),
    produrl character varying(254),
    filesurl character varying(254),
    labelurl character varying(254),
    piloturl character varying(254),
    odeid character varying(20) UNIQUE,
    subsitetag character varying(254),
    geometry geometry(MultiPolygon,900914)
);

CREATE INDEX footprints_instid_index ON footprints (instid);