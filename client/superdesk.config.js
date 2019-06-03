/**
 * This is the default configuration file for the Superdesk application. By default,
 * the app will use the file with the name 'superdesk.config.js' found in the current
 * working directory, but other files may also be specified using relative paths with
 * the SUPERDESK_CONFIG environment variable or the grunt --config flag.
 */
module.exports = function(grunt) {
    return {
        apps: [
             'superdesk-planning'
        ],

        bodyClass: {
            'indent-article': 1
        },

        defaultTimezone: 'Europe/Oslo',

        shortTimeFormat: 'HH:mm, DD.MM.YYYY',
        shortDateFormat: 'HH:mm, DD.MM.YYYY',
        shortWeekFormat: 'HH:mm, DD.MM.YYYY',

        startingDay: '1',

        i18n: 'no',

        view: {
            timeformat: 'HH:mm',
            dateformat: 'DD.MM.YYYY'
        },

        features: {
            preview: 1,
            customAuthoringTopbar: {
                toDesk: true,
                publish: true,
                publishAndContinue: true,
            },
            useTansaProofing: true,
            editFeaturedImage: false,
            hideCreatePackage: true,
            customMonitoringWidget: true,
            scanpixSearchShortcut: true,
            searchShortcut: true,
            noTakes: true,
            noMissingLink: true,
            editor3: true,
            swimlane: {defaultNumberOfColumns: 4},
            noPublishOnAuthoringDesk: true,
            autorefreshContent: true,
        },

        user: {
            'sign_off_mapping': 'email'
        },

        monitoring: {
            'scheduled': true
        },

        workspace: {
            ingest: false,
            content: false,
            tasks: false,
            analytics: false,
            planning: true,
            assignments: true
        },

        ui: {
            publishEmbargo: false,
            publishSendAdnContinue: false,
            italicAbstract: false
        },

        search_cvs: [
            {id: 'ntb_category', name:'Category', field: 'subject', list: 'category'},
            {id: 'subject', name:'Subject', field: 'subject', list: 'subject_custom'}
        ],

        search: {
            'slugline': 1,
            'headline': 1,
            'unique_name': 1,
            'story_text': 1,
            'byline': 1,
            'keywords': 0,
            'creator': 1,
            'from_desk': 1,
            'to_desk': 1,
            'spike': 1,
            'ingest_provider': 1,
            'marked_desks': 1,
            'scheduled': 1
        },

        list: {
            priority: ['urgency'],
            firstLine: [
                'slugline',
                'takekey',
                'highlights',
                'headline',
                'provider',
                'update',
                'updated',
                'state',
                'versioncreated'
            ]
        },

        item_profile: {
            change_profile: 1
        },

        editor: {
            imageDragging: true
        },

        defaultRoute: '/workspace/monitoring',

        langOverride: {
            'en': {
                'ANPA Category': 'Service',
                'ANPA CATEGORY': 'SERVICE'
            }
        },

        tansa: {
            profile: {
                nb: 18,
                nn: 108
            }
        },

        planning_allow_freetext_location: true
    };
};
