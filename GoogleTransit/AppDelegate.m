//
//  AppDelegate.m
//  GoogleTransit
//
//  Created by Simon Maddox on 20/09/2012.
//  Copyright (c) 2012 Simon Maddox. All rights reserved.
//

#import "AppDelegate.h"
#import "LocationSamplePolicy.h"
#import <MapKit/MapKit.h>
#import <CoreLocation/CoreLocation.h>
#import <math.h>

@interface AppDelegate () <CLLocationManagerDelegate>

@property (nonatomic, strong) CLLocationManager *locationManager;
@property (nonatomic, strong) CLLocation *currentLocation;

@property (nonatomic, strong) NSString *currentSource;
@property (nonatomic, strong) NSString *currentDestination;
@property (nonatomic, assign) BOOL currentSourceNeedsLocation;
@property (nonatomic, assign) BOOL currentDestinationNeedsLocation;

@end

@implementation AppDelegate

- (BOOL)application:(UIApplication *)application didFinishLaunchingWithOptions:(NSDictionary *)launchOptions
{
    self.window = [[UIWindow alloc] initWithFrame:[[UIScreen mainScreen] bounds]];
    self.window.backgroundColor = [UIColor blackColor];
    self.window.rootViewController = [[UIViewController alloc] init];
    [self.window makeKeyAndVisible];

	self.locationManager = [[CLLocationManager alloc] init];
	self.locationManager.delegate = self;
	self.locationManager.desiredAccuracy = kCLLocationAccuracyHundredMeters;

    return YES;
}

- (void) applicationDidBecomeActive:(UIApplication *)application
{
	[self startLocationUpdatesIfNeeded];
}

- (void) applicationDidEnterBackground:(UIApplication *)application
{
	[self clearPendingRoute];
}

- (BOOL)application:(UIApplication *)application openURL:(NSURL *)url sourceApplication:(NSString *)sourceApplication annotation:(id)annotation
{
	return [self handleDirectionsURL:url];
}

- (BOOL)application:(UIApplication *)application openURL:(NSURL *)url options:(NSDictionary *)options
{
	return [self handleDirectionsURL:url];
}

- (BOOL) handleDirectionsURL:(NSURL *)url
{
	if ([MKDirectionsRequest isDirectionsRequestURL:url]){
		[self clearPendingRoute];

		MKDirectionsRequest *directionsRequest = [[MKDirectionsRequest alloc] initWithContentsOfURL:url];
		if (!directionsRequest){
			return NO;
		}

		self.currentSourceNeedsLocation = directionsRequest.source.isCurrentLocation;
		self.currentDestinationNeedsLocation = directionsRequest.destination.isCurrentLocation;
		self.currentSource = [self coordinateStringForMapItem:directionsRequest.source];
		self.currentDestination = [self coordinateStringForMapItem:directionsRequest.destination];

		[self startLocationUpdatesIfNeeded];
		[self openTransitDirections];

		return YES;
	}
	return NO;
}

- (void) startLocationUpdatesIfNeeded
{
	if (![self routeNeedsCurrentLocation]){
		return;
	}

	if (![CLLocationManager locationServicesEnabled]){
		[self clearPendingRoute];
		return;
	}

	CLAuthorizationStatus status;
	if (@available(iOS 14.0, *)){
		status = self.locationManager.authorizationStatus;
	} else {
		status = [CLLocationManager authorizationStatus];
	}
	if (status == kCLAuthorizationStatusNotDetermined){
		if ([self.locationManager respondsToSelector:@selector(requestWhenInUseAuthorization)]){
			[self.locationManager requestWhenInUseAuthorization];
		} else {
			[self.locationManager startUpdatingLocation];
		}
		return;
	}

	BOOL authorized = status == kCLAuthorizationStatusAuthorizedAlways ||
		status == kCLAuthorizationStatusAuthorizedWhenInUse;

	if (authorized){
		[self.locationManager startUpdatingLocation];
	} else if (status == kCLAuthorizationStatusDenied ||
			   status == kCLAuthorizationStatusRestricted){
		[self clearPendingRoute];
	}
}

- (BOOL) routeNeedsCurrentLocation
{
	return self.currentSourceNeedsLocation || self.currentDestinationNeedsLocation;
}

- (NSString *) coordinateStringForMapItem:(MKMapItem *)mapItem
{
	if (!mapItem){
		return nil;
	}

	if (mapItem.isCurrentLocation){
		return [self coordinateStringForLocation:self.currentLocation];
	}

	return [self coordinateStringForLocation:mapItem.placemark.location];
}

- (NSString *) coordinateStringForLocation:(CLLocation *)location
{
	if (!location){
		return nil;
	}
	if (!isfinite(location.horizontalAccuracy) || location.horizontalAccuracy < 0){
		return nil;
	}

	CLLocationCoordinate2D coordinate = location.coordinate;
	if (!CLLocationCoordinate2DIsValid(coordinate)){
		return nil;
	}

	return [NSString stringWithFormat:@"%f,%f", coordinate.latitude, coordinate.longitude];
}

- (void) fillCurrentLocationRouteEndpoints
{
	NSString *currentLocationString = [self coordinateStringForLocation:self.currentLocation];
	if (!currentLocationString){
		return;
	}

	if (self.currentSourceNeedsLocation){
		self.currentSource = currentLocationString;
	}

	if (self.currentDestinationNeedsLocation){
		self.currentDestination = currentLocationString;
	}
}

- (void) clearPendingRoute
{
	self.currentSource = nil;
	self.currentDestination = nil;
	self.currentSourceNeedsLocation = NO;
	self.currentDestinationNeedsLocation = NO;
	self.currentLocation = nil;
	[self.locationManager stopUpdatingLocation];
}

- (void) openTransitDirections
{
	[self fillCurrentLocationRouteEndpoints];

	if (!self.currentSource || !self.currentDestination){
		if (![self routeNeedsCurrentLocation]){
			[self clearPendingRoute];
		}
		return;
	}

	NSString *source = [self encodedRouteEndpoint:self.currentSource];
	NSString *destination = [self encodedRouteEndpoint:self.currentDestination];
	if (!source || !destination){
		[self clearPendingRoute];
		return;
	}

	NSString *directionsURLString = [NSString stringWithFormat:@"https://maps.google.com/maps?f=d&source=s_d&saddr=%@&daddr=%@&hl=en&vps=3&jsv=432b&vpsrc=0&gl=us&dirflg=r&ttype=now&noexp=0&noal=0&sort=def&mra=atm&ie=UTF8&ui=maps_mini",
									 source, destination];

	NSURL *directionsURL = [NSURL URLWithString:directionsURLString];

	[self clearPendingRoute];

	[self openURL:directionsURL];
}

- (NSString *) encodedRouteEndpoint:(NSString *)endpoint
{
	if (!endpoint){
		return nil;
	}

	NSString *trimmedEndpoint = [endpoint stringByTrimmingCharactersInSet:[NSCharacterSet whitespaceAndNewlineCharacterSet]];
	if ([trimmedEndpoint length] == 0){
		return nil;
	}

	NSMutableCharacterSet *allowedCharacters = [[NSCharacterSet alphanumericCharacterSet] mutableCopy];
	[allowedCharacters addCharactersInString:@"-._~"];
	return [trimmedEndpoint stringByAddingPercentEncodingWithAllowedCharacters:allowedCharacters];
}

- (void) openURL:(NSURL *)url
{
	if (!url){
		return;
	}

	if (![self isAllowedExternalURL:url]){
		return;
	}

	dispatch_async(dispatch_get_main_queue(), ^{
		UIApplication *application = [UIApplication sharedApplication];
		if ([application canOpenURL:url]){
			[application openURL:url options:@{} completionHandler:nil];
		}
	});
}

- (BOOL) isAllowedExternalURL:(NSURL *)url
{
	return [[url scheme] isEqualToString:@"https"] &&
		[[url host] isEqualToString:@"maps.google.com"] &&
		[[url path] isEqualToString:@"/maps"];
}

- (void)locationManager:(CLLocationManager *)manager
	 didUpdateLocations:(NSArray *)locations
{
	if (![self routeNeedsCurrentLocation]){
		return;
	}

	CLLocation *latestLocation = [LocationSamplePolicy newestUsableLocationFromLocations:locations
																 now:[NSDate date]];
	if (!latestLocation){
		return;
	}

	self.currentLocation = latestLocation;
	[self openTransitDirections];
}

- (void)locationManager:(CLLocationManager *)manager didChangeAuthorizationStatus:(CLAuthorizationStatus)status
{
	[self startLocationUpdatesIfNeeded];
}

- (void)locationManagerDidChangeAuthorization:(CLLocationManager *)manager
{
	[self startLocationUpdatesIfNeeded];
}

- (void)locationManager:(CLLocationManager *)manager didFailWithError:(NSError *)error
{
	if ([[error domain] isEqualToString:kCLErrorDomain] &&
		[error code] == kCLErrorLocationUnknown){
		return;
	}

	[self clearPendingRoute];
}

@end
