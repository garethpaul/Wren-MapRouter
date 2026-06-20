#import <XCTest/XCTest.h>

#import "LocationSamplePolicy.h"

@interface LocationSamplePolicyTests : XCTestCase
@end

@implementation LocationSamplePolicyTests

- (CLLocation *)locationWithLatitude:(CLLocationDegrees)latitude
                           longitude:(CLLocationDegrees)longitude
                  horizontalAccuracy:(CLLocationAccuracy)horizontalAccuracy
                           ageSeconds:(NSTimeInterval)ageSeconds
{
    return [[CLLocation alloc] initWithCoordinate:CLLocationCoordinate2DMake(latitude, longitude)
                                         altitude:0
                               horizontalAccuracy:horizontalAccuracy
                                 verticalAccuracy:0
                                        timestamp:[NSDate dateWithTimeIntervalSinceNow:-ageSeconds]];
}

- (void)testNewestUsableLocationSkipsInvalidTrailingSamples
{
    CLLocation *valid = [self locationWithLatitude:37.7749 longitude:-122.4194 horizontalAccuracy:25 ageSeconds:2];
    CLLocation *invalid = [self locationWithLatitude:NAN longitude:-122.4194 horizontalAccuracy:25 ageSeconds:1];

    CLLocation *selected = [LocationSamplePolicy newestUsableLocationFromLocations:@[valid, invalid]
                                                                                now:[NSDate date]];

    XCTAssertEqual(selected, valid);
}

- (void)testNewestUsableLocationPrefersLatestValidSample
{
    CLLocation *older = [self locationWithLatitude:37.7749 longitude:-122.4194 horizontalAccuracy:25 ageSeconds:2];
    CLLocation *newer = [self locationWithLatitude:37.7750 longitude:-122.4195 horizontalAccuracy:25 ageSeconds:1];

    CLLocation *selected = [LocationSamplePolicy newestUsableLocationFromLocations:@[older, newer]
                                                                                now:[NSDate date]];

    XCTAssertEqual(selected, newer);
}

- (void)testRejectsNonFiniteAccuracy
{
    CLLocation *location = [self locationWithLatitude:37.7749 longitude:-122.4194 horizontalAccuracy:NAN ageSeconds:1];

    XCTAssertFalse([LocationSamplePolicy isUsableLocation:location now:[NSDate date]]);
}

- (void)testRejectsExcessivelyInaccurateLocation
{
    CLLocation *location = [self locationWithLatitude:37.7749 longitude:-122.4194 horizontalAccuracy:1000.1 ageSeconds:1];

    XCTAssertFalse([LocationSamplePolicy isUsableLocation:location now:[NSDate date]]);
}

- (void)testRejectsNonFiniteAge
{
    CLLocation *location = [[CLLocation alloc] initWithCoordinate:CLLocationCoordinate2DMake(37.7749, -122.4194)
                                                          altitude:0
                                                horizontalAccuracy:25
                                                  verticalAccuracy:0
                                                         timestamp:[NSDate dateWithTimeIntervalSince1970:NAN]];

    XCTAssertFalse([LocationSamplePolicy isUsableLocation:location now:[NSDate date]]);
}

- (void)testRejectsStaleAndFutureLocations
{
    NSDate *now = [NSDate date];
    CLLocation *stale = [self locationWithLatitude:37.7749 longitude:-122.4194 horizontalAccuracy:25 ageSeconds:60.1];
    CLLocation *future = [self locationWithLatitude:37.7749 longitude:-122.4194 horizontalAccuracy:25 ageSeconds:-0.1];

    XCTAssertFalse([LocationSamplePolicy isUsableLocation:stale now:now]);
    XCTAssertFalse([LocationSamplePolicy isUsableLocation:future now:now]);
}

- (void)testAcceptsBoundaryAccuracyAndAge
{
    NSDate *now = [NSDate date];
    CLLocation *location = [[CLLocation alloc] initWithCoordinate:CLLocationCoordinate2DMake(37.7749, -122.4194)
                                                          altitude:0
                                                horizontalAccuracy:1000
                                                  verticalAccuracy:0
                                                         timestamp:[now dateByAddingTimeInterval:-60]];

    XCTAssertTrue([LocationSamplePolicy isUsableLocation:location now:now]);
}

@end
