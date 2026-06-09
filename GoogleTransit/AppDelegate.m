//
//  AppDelegate.m
//  GoogleTransit
//
//  Created by Simon Maddox on 20/09/2012.
//  Copyright (c) 2012 Simon Maddox. All rights reserved.
//

#import "AppDelegate.h"
#import <MapKit/MapKit.h>
#import <CoreLocation/CoreLocation.h>

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
    [self.window makeKeyAndVisible];

	self.locationManager = [[CLLocationManager alloc] init];
	self.locationManager.delegate = self;

    return YES;
}

- (void) applicationDidBecomeActive:(UIApplication *)application
{
	[self startLocationUpdatesIfNeeded];
}

- (void) applicationWillResignActive:(UIApplication *)application
{
	[self clearPendingRoute];
}

- (BOOL)application:(UIApplication *)application openURL:(NSURL *)url sourceApplication:(NSString *)sourceApplication annotation:(id)annotation
{
	if ([MKDirectionsRequest isDirectionsRequestURL:url]){

		self.currentSource = nil;
		self.currentDestination = nil;
		self.currentSourceNeedsLocation = NO;
		self.currentDestinationNeedsLocation = NO;

		MKDirectionsRequest *directionsRequest = [[MKDirectionsRequest alloc] initWithContentsOfURL:url];

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

	CLAuthorizationStatus status = [CLLocationManager authorizationStatus];
	if (status == kCLAuthorizationStatusNotDetermined){
		if ([self.locationManager respondsToSelector:@selector(requestWhenInUseAuthorization)]){
			[self.locationManager requestWhenInUseAuthorization];
		} else {
			[self.locationManager startUpdatingLocation];
		}
		return;
	}

	BOOL authorized = status == kCLAuthorizationStatusAuthorized;
#ifdef __IPHONE_8_0
	authorized = authorized ||
		status == kCLAuthorizationStatusAuthorizedAlways ||
		status == kCLAuthorizationStatusAuthorizedWhenInUse;
#endif

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

	if (self.currentSource && self.currentDestination){
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
}

- (NSString *) encodedRouteEndpoint:(NSString *)endpoint
{
	if (!endpoint){
		return nil;
	}

	return [endpoint stringByAddingPercentEscapesUsingEncoding:NSUTF8StringEncoding];
}

- (void) openURL:(NSURL *)url
{
	if (!url){
		return;
	}

	if (![self isAllowedExternalURL:url]){
		return;
	}

	UIApplication *application = [UIApplication sharedApplication];
	if ([application canOpenURL:url]){
		[application openURL:url];
	}
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
	self.currentLocation = [locations lastObject];
	[self openTransitDirections];
}

- (void)locationManager:(CLLocationManager *)manager didChangeAuthorizationStatus:(CLAuthorizationStatus)status
{
	[self startLocationUpdatesIfNeeded];
}

- (void)locationManager:(CLLocationManager *)manager didFailWithError:(NSError *)error
{
	[self clearPendingRoute];
}

@end
