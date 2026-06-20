#import <CoreLocation/CoreLocation.h>

@interface LocationSamplePolicy : NSObject

+ (BOOL)isUsableLocation:(CLLocation *)location now:(NSDate *)now;
+ (CLLocation *)newestUsableLocationFromLocations:(NSArray *)locations now:(NSDate *)now;

@end
