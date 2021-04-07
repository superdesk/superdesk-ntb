import {startApp} from 'superdesk-core/scripts/index';

const planningConfiguration = {
    assignmentsTopBarWidget: true,
};

setTimeout(() => {
    startApp(
        [
            {id: 'auto-tagging-widget', load: () => import('superdesk-core/scripts/extensions/auto-tagging-widget/dist/src/extension').then(res => res.default)},
            {
                id: 'planning-extension',
                load: () =>
                    import('superdesk-planning/client/planning-extension/dist/planning-extension/src/extension')
                        .then((res) => res.default),
                configuration: planningConfiguration,
            },
        ],
        {},
    );
});

export default angular.module('ntb', [])
    .run(['$templateCache', ($templateCache) => {
        // replace core login template with custom
        $templateCache.put(
            'scripts/core/auth/login-modal.html',
            require('./views/login-modal.html'),
        );
    }]);
