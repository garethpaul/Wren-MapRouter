#import <XCTest/XCTest.h>

#import "ExternalDirectionsURLPolicy.h"

@interface ExternalDirectionsURLPolicyTests : XCTestCase
@end

@implementation ExternalDirectionsURLPolicyTests

- (void)testAllowsCanonicalGoogleMapsDirectionsURL
{
    NSURL *url = [NSURL URLWithString:@"https://maps.google.com/maps?saddr=37.7749%2C-122.4194&daddr=37.7750%2C-122.4195"];

    XCTAssertTrue([ExternalDirectionsURLPolicy isAllowedURL:url]);
}

- (void)testRejectsAuthorityDecorationsAndFragments
{
    NSArray *urls = @[
        [NSURL URLWithString:@"https://user@maps.google.com/maps?saddr=a&daddr=b"],
        [NSURL URLWithString:@"https://user:secret@maps.google.com/maps?saddr=a&daddr=b"],
        [NSURL URLWithString:@"https://maps.google.com:443/maps?saddr=a&daddr=b"],
        [NSURL URLWithString:@"https://maps.google.com:444/maps?saddr=a&daddr=b"],
        [NSURL URLWithString:@"https://maps.google.com/maps?saddr=a&daddr=b#fragment"]
    ];

    for (NSURL *url in urls){
        XCTAssertFalse([ExternalDirectionsURLPolicy isAllowedURL:url]);
    }

    XCTAssertFalse([ExternalDirectionsURLPolicy isAllowedURL:nil]);
}

@end
