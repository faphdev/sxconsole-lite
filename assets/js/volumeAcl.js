/**
 * @file Provides components for a volume page.
 */
var React = require('react'),
    ReactDOM = require('react-dom'),
    cookies = require('browser-cookies');


/**
 * @classdesc Displays volume users and their permissions.
 */
var VolumeUsers = React.createClass({
    propTypes: {
        setPermUrl: React.PropTypes.string.isRequired,
        perms: React.PropTypes.array.isRequired
    },
    getInitialState: function () {
        return {
            pendingRequests: {},
            userList: _.map(this.props.perms, 'email'),
            perms: _.keyBy(this.props.perms, 'email'),
        };
    },

    render: function () {
        var list = this.state.userList,
            noUsers = (
                <span className="text-muted">
                    {__("There are no users yet")}
                </span>);
        return (_.isEmpty(list)) ? noUsers : this.renderPermTable(list);
    },
    renderPermTable: function (list) {
        return (
            <table className='table table-striped'>
                <thead>
                    <tr>
                        <th>{__("Username")}</th>
                        <th className='text-right'>{__("Permissions")}</th>
                    </tr>
                </thead>
                <tbody>
                    { list.map(this.renderPerm, this) }
                </tbody>
            </table>)
    },
    renderPerm: function (email) {
        var perm = this.state.perms[email];
        return (
            <tr key={perm.email}>
                <td>{perm.email}</td>
                <td className='text-right'>
                    <div className='btn-group'>
                        { this.renderPermBtn(perm, 'read') }
                        { this.renderPermBtn(perm, 'write') }
                        { this.renderPermBtn(perm, 'manager') }
                    </div>
                </td>
            </tr>);
    },
    renderPermBtn: function (perm, type) {
        var email = perm.email,
            btnClass = 'btn ' + (perm[type] ? 'btn-success' : 'btn-default'),
            typeName = {
                read: __("Read"),
                write: __("Write"),
                manager: __("Manager"),
            }[type],
            typeDesc = {
                read: __("The user can read files on the volume"),
                write: __("The user can modify files on the volume"),
                manager: __("The user can manage permissions of other users on this volume"),
            }[type];
        return (
            <button key={permKey(email, type)} className={btnClass} type='button'
                    disabled={this.state.pendingRequests[permKey(email, type)]}
                    style={{cursor: 'pointer'}}  // Override cursor for disabled buttons
                    title={typeDesc}
                    disabled={perm.is_reserved}
                    onClick={this.getButtonHandler(email, type)}>
                {typeName}
            </button>);
    },

    getButtonHandler(email, type) {
        return function () {
            /* register this to pendingRequests */
            this.state.pendingRequests[permKey(email, type)] = true;
            this.setState({pendingRequests: this.state.pendingRequests});

            var options = {
                    method: 'POST',
                    url: this.props.setPermUrl,
                    data: {
                        csrfmiddlewaretoken: cookies.get('csrftoken'),
                        email: email,
                        perm: type,
                        value: !this.state.perms[email][type]
                    }
                };

            /* Update perm on success */
            options.success = function (data) {
                this.state.perms[email] = data;
                this.setState({perms: this.state.perms});
            }.bind(this);

            /* When the request finishes, remove this from pendingRequests */
            options.complete = function () {
                this.state.pendingRequests[permKey(email, type)] = false;
                this.setState({pendingRequests: this.state.pendingRequests});
            }.bind(this);

            /* Send the request */
            $.ajax(options);
        }.bind(this);
    }
})

/* Return an identificator for user permission */
function permKey (email, type) { return email + '-' + type; };

// Initialize and render the component
var mount = document.getElementById('volume-users'),
    data = JSON.parse(mount.dataset.init);
ReactDOM.render(<VolumeUsers {...data} />, mount);
