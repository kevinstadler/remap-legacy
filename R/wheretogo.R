# tz <- "GMT"
d <- jsonlite::fromJSON("LocationHistory.json")$location
d$timestamp <- as.numeric(d$timestampMs)/1000

# names(d)
datasetrange <- as.POSIXlt(range(d$timestamp), origin="1970-01-01")

# select all data points from the given time period (24hrs by default)
selectday <- function(start, end=start+24*60*60) {
  subset(d, timestamp >= start & timestamp < end)
}

# ... for extra arguments like tz
daysequence <- function(from="2015-01-01", to="2015-12-31", ...)
  seq(as.POSIXct(from, ...), as.POSIXct(to, ...), by="days")

daysequence()
