#import "ExternalDirectionsURLPolicy.h"

@implementation ExternalDirectionsURLPolicy

+ (BOOL)isAllowedURL:(NSURL *)url
{
    return url != nil &&
        [[url scheme] isEqualToString:@"https"] &&
        [[url host] isEqualToString:@"maps.google.com"] &&
        [[url path] isEqualToString:@"/maps"] &&
        [url user] == nil &&
        [url password] == nil &&
        [url port] == nil &&
        [url fragment] == nil;
}

@end
