#import "LocationSamplePolicy.h"

#import <math.h>

static const NSTimeInterval LocationSampleMaximumAge = 60;
static const CLLocationAccuracy LocationSampleMaximumHorizontalAccuracy = 1000;

@implementation LocationSamplePolicy

+ (BOOL)isUsableLocation:(CLLocation *)location now:(NSDate *)now
{
    if (!location || !now){
        return NO;
    }

    CLLocationCoordinate2D coordinate = location.coordinate;
    if (!CLLocationCoordinate2DIsValid(coordinate) ||
        !isfinite(coordinate.latitude) ||
        !isfinite(coordinate.longitude)){
        return NO;
    }

    if (!isfinite(location.horizontalAccuracy) ||
        location.horizontalAccuracy < 0 ||
        location.horizontalAccuracy > LocationSampleMaximumHorizontalAccuracy){
        return NO;
    }

    NSTimeInterval locationAge = [now timeIntervalSinceDate:location.timestamp];
    if (!isfinite(locationAge) ||
        locationAge < 0 ||
        locationAge > LocationSampleMaximumAge){
        return NO;
    }

    return YES;
}

+ (CLLocation *)newestUsableLocationFromLocations:(NSArray *)locations now:(NSDate *)now
{
    for (CLLocation *location in [locations reverseObjectEnumerator]){
        if ([self isUsableLocation:location now:now]){
            return location;
        }
    }
    return nil;
}

@end
