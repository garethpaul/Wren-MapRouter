#import <Foundation/Foundation.h>

@interface ExternalDirectionsURLPolicy : NSObject

+ (BOOL)isAllowedURL:(NSURL *)url;

@end
