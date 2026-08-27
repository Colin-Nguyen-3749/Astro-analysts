# Characterizing Astrometric Solution Failures in the LCO Imaging Archive

## Team: Astro Analysts
## Andrew Church, Colin Nguyen, Han Nguyen, Ollie Morse

### Abstract
\{write this later\}

### Introduction
\{Note: for now, this will help with our own understanding, but it will most likely need to be rewritten and polished towards the finishing-up of our project\}
As a nonprofit science institute that operates fully robotically, LCO's main purpose of observing brief astronomical events through the use of imaging from telescopes does not come without issues. Our team was approached by Las Cumbres Observatory (LCO) for help with one of their continual problems: astrometric failure. 

Astrometric failure is a problem with data quality, where images that can't be mapped to sky coordinates are made useless for most scientific needs. While our client knows of this issue, they want our team to answer the following questions: 

1. Out of all images, what percentage of them fail?
2. What factors, like location, filter, or exposure time, affect this percentage?
3. What factors can tell us what images will fail?

To investigate this, our team will utilize the public LCO science archive along with its API. We will also create a data set of the image frames with their header metadata as well. 

Finally, our team will take our research further by advising LCO on what it could do with the data insights that we pulled for them. 

### Methods
For this project, our analysis will be done using Python along with the Astropy package. 

### Goals
- [ ] Create a reproduceable dataset of the image frame metadata, which will be taken from the public LCO archive through its API
   - [ ] Document our sampling strategy that doesn't break the archive's daily API request limit
- [ ] Measure the astrometric failure rate
   - [ ] Break down these numbers by site, telescope class, instrument, filter, and exposure time
- [ ] Find if the failure rate varies by time of year or over the network's life
   - [ ] See if any shifts in failure rates match up with changes in pipeline or hardware
- [ ] Clearly define what factors set apart a failed image from a successful image
   - [ ] Use the method of testing hypotheses
- [ ] Come up with statistical test, machine learning methods, or predictive analytic methods that LCO could use to mark images at risk of failure
   - [ ] Analyze the effectiveness and quality of each approach 
- [ ] Document everything for reproducibility

### Secondary Goals
- [ ] Inspect images (visually) to find any failures that were not captured by image metadata
- [ ] Recommend what LCO could do to make these future failures easier to predict and find
- [ ] See if the public archive is good enough for our needs, or if we need use proprietary data
