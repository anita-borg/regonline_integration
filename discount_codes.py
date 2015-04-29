#!/usr/bin/env python

import json
import logging
import random
import uuid

from datastore import get_discount_codes

badge_types = {
    "general_full"  : { 'name'          : 'General',
                        'product_code'  : 'GHP5G',
                        'regonline_url' : '[To Be Determined]',
                        'reserve_spot'  : True,
                        'regonline_str' : '-100%' },
    "student_full"  : { 'name'          : 'Student',
                        'product_code'  : 'GHP5A',
                        'regonline_url' : '[To Be Determined]',
                        'reserve_spot'  : True,
                        'regonline_str' : '-100%' },
    "academic_full" : { 'name'          : 'Academic',
                        'product_code'  : 'GHP5A',
                        'regonline_url' : '[To Be Determined]',
                        'reserve_spot'  : True,
                        'regonline_str' : '-100%' },
    "transition_full" : { 'name'          : 'Transition',
                          'product_code'  : 'GHP5C',
                          'regonline_url' : '[To Be Determined]',
                          'reserve_spot'  : True,
                        'regonline_str' : '-100%' },
    "general_1"     : { 'name'          : 'General One Day',
                        'product_code'  : 'GHP5G',
                        'regonline_url' : '[To Be Determined]',
                        'reserve_spot'  : True,
                        'regonline_str' : '-100%' },
    "speaker_full"  : { 'name'          : 'Speaker Full Conference',
                        'product_code'  : 'GHP5G',
                        'regonline_url' : '[To Be Determined]',
                        'reserve_spot'  : True,
                        'regonline_str' : '-100%' },
    "speaker_1"     : { 'name'          : 'Speaker One Day',
                        'product_code'  : 'GHP5G',
                        'regonline_url' : '[To Be Determined]',
                        'reserve_spot'  : True,
                        'regonline_str' : '-100%' },
    "booth"         : { 'name'          : 'Booth Staff Only',
                        'product_code'  : 'GHP5B',
                        'regonline_url' : '[To Be Determined]',
                        'reserve_spot'  : True,
                        'summary_group' : 'Corporate',
                        'regonline_str' : '-100%' },
    "student_20"    : { 'name'          : 'Student 20% Off',
                        'product_code'  : 'GHP5S',
                        'regonline_url' : '[To Be Determined]',
                        'reserve_spot'  : False,
                        'regonline_str' : '-20%' },
    "student_15"    : { 'name'          : 'Student 15% Off',
                        'product_code'  : 'GHP5S',
                        'regonline_url' : '[To Be Determined]',
                        'reserve_spot'  : False,
                        'regonline_str' : '-15%' },
    "student_10"    : { 'name'          : 'Student 10% Off',
                        'product_code'  : 'GHP5S',
                        'regonline_url' : '[To Be Determined]',
                        'reserve_spot'  : False,
                        'regonline_str' : '-10%' },
}

sponsor_reporting_groups = {
    'ABI Partners Only - Diamond'  : 'Corporate',
    'ABI Partners Only - Platinum' : 'Corporate',
    'Corporate - Gold'             : 'Corporate', 
    'Corporate - Silver'           : 'Corporate', 
    'Academic - Gold'              : 'Academic', 
    'Academic - Silver'            : 'Academic', 
    'Academic - Bronze'            : 'Academic', 
    'Lab & Non-Profit - Gold'      : 'Lab and Non-Profit', 
    'Lab & Non-Profit - Silver'    : 'Lab and Non-Profit', 
    'Lab & Non-Profit - Bronze'    : 'Lab and Non-Profit', 
     # DEBUG - this one doesn't really have an affiliation, we'll lump
     # it in with corporate.
    'GHC Event Sponsorships and Enterprise Packages' : 'Corporate',
    'Show Management'              : 'Show Management',
 }

sponsor_entitlements_2015 = {
    'ABI Partners Only - Diamond'  : [
        { 'badge_type' : 'general_full',
          'quantity' : 20, },
        { 'badge_type' : 'booth',
          'quantity' : 8, },
    ],
    'ABI Partners Only - Platinum' : [ 
        { 'badge_type' : 'general_full',
          'quantity' : 10, },
        { 'badge_type' : 'booth',
          'quantity' : 4, },
    ],
    'Corporate - Gold'             : [ 
        { 'badge_type' : 'general_full',
          'quantity' : 5, },
        { 'badge_type' : 'booth',
          'quantity' : 3, },
    ],
    'Corporate - Silver'           : [ 
        { 'badge_type' : 'general_full',
          'quantity' : 3, },
        { 'badge_type' : 'booth',
          'quantity' : 2, },
    ],
    'Academic - Gold'              : [ 
        { 'badge_type' : 'academic_full',
          'quantity' : 3, },
        { 'badge_type' : 'student_20',
          'quantity' : 100, },
    ],
    'Academic - Silver'            : [ 
        { 'badge_type' : 'academic_full',
          'quantity' : 2, },
        { 'badge_type' : 'student_15',
          'quantity' : 50, },
    ],
    'Academic - Bronze'            : [ 
        { 'badge_type' : 'academic_full',
          'quantity' : 1, },
        { 'badge_type' : 'student_10',
          'quantity' : 25, },
    ],
    'Lab & Non-Profit - Gold'      : [ 
        { 'badge_type' : 'general_full',
          'quantity' : 3, },
    ],
    'Lab & Non-Profit - Silver'    : [ 
        { 'badge_type' : 'general_full',
          'quantity' : 2, },
    ],
    'Lab & Non-Profit - Bronze'    : [ 
        { 'badge_type' : 'general_full',
          'quantity' : 1, },
    ],
}

def get_badge_types( eventID=None ):
    # We only have one set of badge types, so ignore the eventID for now.
    return badge_types

def get_sponsor_reporting_groups( eventID=None ):
    # We only have one set of spornsor reporting groups, so ignore the eventID for now.
    return sponsor_reporting_groups

def generate_discount_codes( eventID, sponsor, all_existing_codes ):
    '''Takes in eventID and a sponsor object which can be either a suds
    object or a sponsor like hash from get_sponsors.

    Takes a list argument of all existing discount codes for that
    event.
    '''

    all_existing_code_values = { x['discount_code']:True for x in all_existing_codes }
    
    discount_codes = []

    if sponsor['RegistrationType'] in sponsor_entitlements_2015:
        for entitlement in sponsor_entitlements_2015[sponsor['RegistrationType']]:
            discount_code = {
                'SponsorID'        : sponsor['ID'],
                'RegTypeID'        : sponsor['RegTypeID'],
                'RegistrationType' : sponsor['RegistrationType'],
            }

            discount_code['ID'] = str( uuid.uuid4() )

            discount_code['badge_type'] = entitlement['badge_type']
            discount_code['regonline_str'] = badge_types[entitlement['badge_type']]['regonline_str']
            discount_code['quantity'] = entitlement['quantity']
            # Get rid of any unicode stuff we don't want.
            company_abbr = sponsor['Company'].encode( 'ascii', 'ignore' ).lower()
            
            skip_chars = [ 'a', 'e', 'i', 'o', 'u', 'l' ]
            company_abbr = ''.join( [ c for c in company_abbr if ( ( c.isalnum() ) and ( c not in skip_chars ) ) ] )
            company_abbr = company_abbr.ljust( 4, '0' )
            company_abbr = company_abbr[:4]

            unique = False
            while not unique:
                random_string = get_random_string( 3 )
                new_discount_code = "%s%s%03d" % ( company_abbr, random_string, entitlement['quantity'] )
                new_discount_code = new_discount_code.replace( '0', 'a' )
                new_discount_code = new_discount_code.replace( '1', 'b' )
                if new_discount_code not in all_existing_code_values:
                    unique = True
                else:
                    # We had a duplicate collision, try again with a new random string.
                    pass

            discount_code['discount_code'] = new_discount_code
            discount_codes.append( discount_code )
            logging.info( json.dumps( { 'message' : "Created new discount_code: %s" % ( new_discount_code ),
                                        'discount_code_data' : discount_code } ) )
    else:
        error_message = "No sponsor codes found for registration type: %s" % ( sponsor['RegistrationType'] )
        logging.error( json.dumps( { 'message' : error_message } ) )
        raise Exception( error_message )
    
    return discount_codes

def get_random_string( length ):
    '''Return a random string of length'''
    alphabet = "bcdfghjkmnpqrstvwxyz23456789"
    
    result = ""
    for i in range( length ):
        result += random.choice( alphabet )
        
    return result
        
def generate_discount_code( eventID, sponsor, badge_type, quantity, all_existing_codes ):
    '''Takes in eventID and a sponsor object which can be either a suds
    object or a sponsor like hash from get_sponsors.

    Takes a list argument of all existing discount codes for that
    event.
    '''

    all_existing_code_values = { x['discount_code']:True for x in all_existing_codes }
    
    discount_code = {
        'SponsorID'        : sponsor['ID'],
        'RegTypeID'        : sponsor['RegTypeID'],
        'RegistrationType' : sponsor['RegistrationType'],
    }

    discount_codes = []

    discount_code['ID'] = str( uuid.uuid4() )

    discount_code['badge_type'] = badge_type
    discount_code['regonline_str'] = badge_types[badge_type]['regonline_str']
    discount_code['quantity'] = quantity
    # Get rid of any unicode stuff we don't want.
    company_abbr = sponsor['Company'].encode( 'ascii', 'ignore' ).lower()
            
    # Avoid ambiguous characters and non-alphanumeric characters.
    skip_chars = [ 'a', 'e', 'i', 'o', 'u', 'l' ]
    company_abbr = ''.join( [ c for c in company_abbr if ( ( c.isalnum() ) and ( c not in skip_chars ) ) ] )
    company_abbr = company_abbr.ljust( 4, '0' )
    company_abbr = company_abbr[:4]

    unique = False
    while not unique:
        random_string = get_random_string( 3 )
        new_discount_code = "%s%s%03d" % ( company_abbr, random_string, quantity )
        new_discount_code = new_discount_code.replace( '0', 'a' )
        new_discount_code = new_discount_code.replace( '1', 'b' )
        if new_discount_code not in all_existing_code_values:
            unique = True
        else:
            # We had a duplicate collision, try again with a new random string.
            pass

    discount_code['discount_code'] = new_discount_code

    logging.info( json.dumps( { 'message' : "Created new discount_code: %s" % ( new_discount_code ),
                                'discount_code_data' : discount_code } ) )

    return discount_code
