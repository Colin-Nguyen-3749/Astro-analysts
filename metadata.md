
| Variable Name | Data Type | Classification | Meaning |
| :---     | :---:    | :---:  | :---   |
| id     | int64   | Categorical (Nominal)   |  An 8-digit figure that represents a unique image frame     |        
| basename     | object (string)    | Categorical (Nominal)   | The base of the filename without a file extension.          |
| observation_date     |  object (string)      | Categorical (Nominal)     | The UTC time at the start of exposure         |      
| site_id     |  object (string)      | Categorical (Nominal)     |   The site that produced this frame       |          
| telescope_id     |  object (string)      | Categorical (Nominal)    |  The site that produced this frame      |          
| instrument_id     |  object (string)      | Categorical (Nominal)     |  Unique values for frames taken with this instrument        |          
| WCSERR     | int64     | Categorical (Nominal)     |  Error status of WCS fit. 0 for no error. 4 for failure        |          
| SATFRAC     | float64     | Numeric (Ratio)    |  The degree of saturation in a unique image frame        |          
| EXPTIME     | float64     | Numeric (Ratio)    | The actual exposure time. Strictly, the difference between the time when the shutter closes (UTSTOP) and when the shutter opens (UTSTART). Before 2019-04-10, EXPTIME was the requested exposure time for 2m and 1m observations         |         
| FILTER     | object (string)  |  Categorical (Nominal)    | Concatenation of FILTER1--3, asterisk '*' separated list of all non air/clear filter                 |
| AIRMASS     | float64     | Numeric (Ratio)      | Effective mean airmass (mean airmass for the center of the frame) (Amount of atmosphere that star light has to travel through to reach the telescope)         |          
| L1FWHM     | float64     | Numeric (Ratio)      | Frame FWHM; Median FWHM of all sources extracted with astropy's photutils algorithm, after very small sources (<9 pix) and sources with FLAGS != 0 have been removed. For individual sources, the FWHM is the 90th percentile of the distribution of distances from the source center to the half-maximum contour. (Full Width at Half Maximum: If the brightness emitted by a star is mapped on a normal curve, you take half the maximum still at full width, to account for high saturation. It’s like standardization.)         |          
| MOONFRAC     | float64     | Numeric (Ratio)      | Meaning Fraction of the moon illuminated: Fraction of the moon illuminated Ranges from 0.0 (New Moon) to 1.0 (Full Moon)               
| MOONDIST     | float64     | Numeric (Ratio)      | Lunar distance from target |          
| SKYMAG     | float64     | Numeric (Ratio)      | Computed (expected) sky brightness |          
| WMSHUMID(%)     | float64     | Numeric (Ratio)      |  Current percentage humidity|          
| WMSTEMP     | float64     | Numeric (Ratio)      | External temperature (in Celsius)         |          
| PIXSCALE     | float64     | Numeric (Ratio)      |  Nominal pixel scale on the sky |          
